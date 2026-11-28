-- PRE Kanban sync lifecycle, atomic claim, and transactional item application.
alter table public.kanban_sync_runs
  add column if not exists claimed_at timestamptz;
alter table public.kanban_sync_runs
  add column if not exists claim_token uuid;

create or replace function public.kanban_claim_sync_run(
  p_sync_run_id uuid,
  p_expected_digest text,
  p_claim_token uuid
)
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog
as $$
declare
  v_run public.kanban_sync_runs;
  v_failed integer;
begin
  select * into v_run
  from public.kanban_sync_runs
  where id = p_sync_run_id
  for update;

  if not found then
    raise exception 'sync_run_not_found' using errcode = 'P0002';
  end if;
  if p_claim_token is null then
    raise exception 'sync_claim_token_required' using errcode = '22023';
  end if;
  if auth.uid() is null
     or not kanban_private.has_workspace_role(v_run.workspace_id, array['owner','admin','editor']) then
    raise exception 'sync_run_write_forbidden' using errcode = '42501';
  end if;
  if p_expected_digest is null or v_run.payload_digest <> p_expected_digest then
    raise exception 'preview_digest_mismatch' using errcode = '22023';
  end if;

  if v_run.status = 'APPLYING'
     and v_run.claimed_at < now() - interval '5 minutes' then
    update public.kanban_sync_runs
    set claimed_at = now(), claim_token = p_claim_token
    where id = v_run.id;
    return jsonb_build_object(
      'status','APPLYING',
      'sync_run_id',v_run.id,
      'claim_token',p_claim_token,
      'reclaimed',true
    );
  end if;

  v_failed := coalesce((v_run.result_summary ->> 'failed')::integer, 0);
  if v_run.status = 'PARTIAL'
     and v_failed > 0
     and (v_run.claimed_at is null or v_run.claimed_at < now() - interval '5 minutes') then
    update public.kanban_sync_runs
    set status = 'APPLYING', claimed_at = now(), claim_token = p_claim_token
    where id = v_run.id;
    return jsonb_build_object(
      'status','APPLYING',
      'sync_run_id',v_run.id,
      'claim_token',p_claim_token,
      'reclaimed',true,
      'retry',true
    );
  end if;

  if v_run.status <> 'PREVIEWED' then
    raise exception 'sync_run_not_claimable:%', v_run.status using errcode = '55000';
  end if;

  if v_run.expires_at <= now() then
    update public.kanban_sync_runs
    set status = 'EXPIRED'
    where id = v_run.id;
    return jsonb_build_object('status','EXPIRED','sync_run_id',v_run.id);
  end if;

  update public.kanban_sync_runs
  set status = 'APPLYING', claimed_at = now(), claim_token = p_claim_token
  where id = v_run.id and status = 'PREVIEWED';

  return jsonb_build_object(
    'status','APPLYING',
    'sync_run_id',v_run.id,
    'claim_token',p_claim_token,
    'reclaimed',false
  );
end;
$$;
revoke all on function public.kanban_claim_sync_run(uuid,text,uuid) from public,anon;
grant execute on function public.kanban_claim_sync_run(uuid,text,uuid) to authenticated;

create or replace function public.kanban_apply_sync_item(
  p_sync_run_id uuid,
  p_claim_token uuid,
  p_item_payload jsonb
)
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog
as $$
declare
  v_run public.kanban_sync_runs;
  v_binding public.kanban_sync_bindings;
  v_card public.kanban_cards;
  v_action text;
  v_source_id text;
  v_digest text;
  v_column_id uuid;
  v_expected_revision integer;
  v_position numeric;
  v_metadata jsonb;
  v_disposition text;
begin
  select * into v_run
  from public.kanban_sync_runs
  where id = p_sync_run_id
  for share;

  if not found then
    raise exception 'sync_run_not_found' using errcode = 'P0002';
  end if;
  if v_run.status <> 'APPLYING' then
    raise exception 'sync_run_not_applying' using errcode = '55000';
  end if;
  if p_claim_token is null or v_run.claim_token is distinct from p_claim_token then
    raise exception 'sync_claim_token_mismatch' using errcode = '42501';
  end if;
  if auth.uid() is null
     or not kanban_private.has_workspace_role(v_run.workspace_id, array['owner','admin','editor']) then
    raise exception 'sync_item_write_forbidden' using errcode = '42501';
  end if;

  v_action := p_item_payload ->> 'action';
  v_source_id := p_item_payload ->> 'source_work_item_id';
  v_digest := p_item_payload ->> 'source_digest';

  if v_source_id is null
     or v_digest is null
     or v_digest !~ '^[a-f0-9]{64}$' then
    raise exception 'invalid_sync_item_identity_or_digest' using errcode = '22023';
  end if;

  if not exists (
    select 1
    from jsonb_array_elements(coalesce(v_run.preview_plan -> 'items', '[]'::jsonb)) as approved(item)
    where approved.item = p_item_payload
  ) then
    raise exception 'sync_item_not_part_of_approved_preview' using errcode = '42501';
  end if;

  -- Serialize same-board writes so computed ordering and WIP checks do not race.
  perform 1
  from public.kanban_boards
  where id = v_run.board_id and workspace_id = v_run.workspace_id
  for update;

  if not found then
    raise exception 'sync_board_not_found' using errcode = 'P0002';
  end if;

  if v_action = 'CREATE' then
    select * into v_binding
    from public.kanban_sync_bindings
    where workspace_id = v_run.workspace_id
      and source_system = v_run.source_system
      and source_work_item_id = v_source_id
    for update;

    if found then
      if v_binding.last_source_digest = v_digest then
        return jsonb_build_object(
          'disposition','NOOP',
          'card_id',v_binding.card_id,
          'source_work_item_id',v_source_id
        );
      end if;
      return jsonb_build_object(
        'disposition','CONFLICT',
        'reason','source_binding_already_exists_with_different_digest',
        'card_id',v_binding.card_id
      );
    end if;

    v_column_id := (p_item_payload ->> 'column_id')::uuid;
    if not exists (
      select 1
      from public.kanban_columns
      where id = v_column_id
        and board_id = v_run.board_id
        and workspace_id = v_run.workspace_id
        and not is_archived
    ) then
      return jsonb_build_object(
        'disposition','CONFLICT',
        'reason','target_column_missing_or_outside_board'
      );
    end if;

    select coalesce(max(position),0) + 1000
    into v_position
    from public.kanban_cards
    where board_id = v_run.board_id
      and column_id = v_column_id
      and not is_archived;

    v_metadata := jsonb_build_object(
      'source_system',v_run.source_system,
      'evidence_refs',coalesce(p_item_payload -> 'evidence_refs','[]'::jsonb),
      'dependencies',coalesce(p_item_payload -> 'dependencies','[]'::jsonb)
    ) || coalesce(p_item_payload -> 'extra','{}'::jsonb);

    insert into public.kanban_cards(
      workspace_id,board_id,column_id,title,description,priority,
      acceptance_criteria,position,metadata,created_by,updated_by
    ) values (
      v_run.workspace_id,
      v_run.board_id,
      v_column_id,
      p_item_payload ->> 'title',
      p_item_payload ->> 'description',
      coalesce(p_item_payload ->> 'priority','medium'),
      p_item_payload ->> 'acceptance_criteria',
      v_position,
      v_metadata,
      auth.uid(),
      auth.uid()
    )
    returning * into v_card;

    insert into public.kanban_sync_bindings(
      workspace_id,board_id,card_id,source_system,source_work_item_id,
      source_revision,last_source_digest,last_board_revision,sync_direction
    ) values (
      v_run.workspace_id,
      v_run.board_id,
      v_card.id,
      v_run.source_system,
      v_source_id,
      p_item_payload ->> 'source_revision',
      v_digest,
      v_card.revision,
      v_run.direction
    );

    v_disposition := 'CREATED';

  elsif v_action = 'UPDATE' then
    select * into v_binding
    from public.kanban_sync_bindings
    where workspace_id = v_run.workspace_id
      and source_system = v_run.source_system
      and source_work_item_id = v_source_id
    for update;

    if not found then
      return jsonb_build_object('disposition','CONFLICT','reason','source_binding_missing');
    end if;

    select * into v_card
    from public.kanban_cards
    where id = v_binding.card_id and board_id = v_run.board_id
    for update;

    if not found or v_card.is_archived then
      return jsonb_build_object('disposition','CONFLICT','reason','bound_card_missing_or_archived');
    end if;

    if v_binding.last_source_digest = v_digest then
      if v_card.revision = v_binding.last_board_revision then
        return jsonb_build_object(
          'disposition','NOOP',
          'card_id',v_card.id,
          'card_revision',v_card.revision,
          'source_work_item_id',v_source_id
        );
      end if;
      return jsonb_build_object(
        'disposition','CONFLICT',
        'reason','board_card_changed_since_last_sync',
        'card_id',v_card.id,
        'current_revision',v_card.revision
      );
    end if;

    v_expected_revision := (p_item_payload ->> 'expected_revision')::integer;
    if v_card.revision <> v_expected_revision
       or v_binding.last_board_revision <> v_expected_revision then
      return jsonb_build_object(
        'disposition','CONFLICT',
        'reason','board_card_revision_changed',
        'expected_revision',v_expected_revision,
        'actual_revision',v_card.revision
      );
    end if;

    v_column_id := (p_item_payload ->> 'column_id')::uuid;
    if not exists (
      select 1
      from public.kanban_columns
      where id = v_column_id
        and board_id = v_run.board_id
        and workspace_id = v_run.workspace_id
        and not is_archived
    ) then
      return jsonb_build_object(
        'disposition','CONFLICT',
        'reason','target_column_missing_or_outside_board'
      );
    end if;

    perform set_config('kanban.suppress_outbox','on',true);

    v_metadata := jsonb_build_object(
      'source_system',v_run.source_system,
      'evidence_refs',coalesce(p_item_payload -> 'evidence_refs','[]'::jsonb),
      'dependencies',coalesce(p_item_payload -> 'dependencies','[]'::jsonb)
    ) || coalesce(p_item_payload -> 'extra','{}'::jsonb);

    update public.kanban_cards
    set column_id = v_column_id,
        title = p_item_payload ->> 'title',
        description = p_item_payload ->> 'description',
        priority = coalesce(p_item_payload ->> 'priority','medium'),
        acceptance_criteria = p_item_payload ->> 'acceptance_criteria',
        metadata = v_metadata,
        updated_by = auth.uid()
    where id = v_card.id
    returning * into v_card;

    update public.kanban_sync_bindings
    set source_revision = p_item_payload ->> 'source_revision',
        last_source_digest = v_digest,
        last_board_revision = v_card.revision,
        last_synced_at = now()
    where id = v_binding.id;

    v_disposition := 'UPDATED';
  else
    raise exception 'unsupported_sync_action:%',v_action using errcode = '22023';
  end if;

  insert into public.kanban_sync_events(
    workspace_id,sync_run_id,source_system,source_work_item_id,event_type,
    disposition,details,actor_user_id
  ) values (
    v_run.workspace_id,
    v_run.id,
    v_run.source_system,
    v_source_id,
    v_action,
    v_disposition,
    jsonb_build_object(
      'card_id',v_card.id,
      'card_revision',v_card.revision,
      'source_digest',v_digest
    ),
    auth.uid()
  );

  return jsonb_build_object(
    'disposition',v_disposition,
    'card_id',v_card.id,
    'card_revision',v_card.revision,
    'source_work_item_id',v_source_id
  );
end;
$$;
revoke all on function public.kanban_apply_sync_item(uuid,uuid,jsonb) from public,anon;
grant execute on function public.kanban_apply_sync_item(uuid,uuid,jsonb) to authenticated;

comment on function public.kanban_apply_sync_item(uuid,uuid,jsonb) is
  'Applies one exact preview item and its binding/event in one Postgres transaction. The function checks workspace role and serializes work on the board.';

create or replace function public.kanban_finalize_sync_run(
  p_sync_run_id uuid,
  p_claim_token uuid,
  p_applied_count integer,
  p_conflict_count integer,
  p_result_summary jsonb
)
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog
as $$
declare
  v_run public.kanban_sync_runs;
  v_failed integer;
  v_status text;
begin
  select * into v_run
  from public.kanban_sync_runs
  where id = p_sync_run_id
  for update;

  if not found then
    raise exception 'sync_run_not_found' using errcode = 'P0002';
  end if;
  if auth.uid() is null
     or not kanban_private.has_workspace_role(v_run.workspace_id, array['owner','admin','editor']) then
    raise exception 'sync_run_finalize_forbidden' using errcode = '42501';
  end if;
  if v_run.status <> 'APPLYING' then
    raise exception 'sync_run_not_applying' using errcode = '55000';
  end if;
  if p_claim_token is null or v_run.claim_token is distinct from p_claim_token then
    raise exception 'sync_claim_token_mismatch' using errcode = '42501';
  end if;
  if p_applied_count is null
     or p_conflict_count is null
     or p_applied_count < 0
     or p_conflict_count < 0
     or p_applied_count > v_run.source_count
     or p_conflict_count > v_run.source_count
     or jsonb_typeof(p_result_summary) <> 'object' then
    raise exception 'invalid_sync_finalization_payload' using errcode = '22023';
  end if;

  v_failed := coalesce((p_result_summary ->> 'failed')::integer,0);
  if v_failed < 0
     or v_failed > v_run.source_count
     or p_applied_count + p_conflict_count + v_failed > v_run.source_count then
    raise exception 'invalid_sync_failure_count' using errcode = '22023';
  end if;

  v_status := case
    when p_conflict_count > 0 or v_failed > 0 then 'PARTIAL'
    else 'APPLIED'
  end;

  update public.kanban_sync_runs
  set status = v_status,
      applied_count = p_applied_count,
      conflict_count = p_conflict_count,
      result_summary = p_result_summary,
      applied_at = now()
  where id = v_run.id;

  return jsonb_build_object('run_id',v_run.id,'status',v_status);
end;
$$;
revoke all on function public.kanban_finalize_sync_run(uuid,uuid,integer,integer,jsonb) from public,anon;
grant execute on function public.kanban_finalize_sync_run(uuid,uuid,integer,integer,jsonb) to authenticated;

comment on function public.kanban_finalize_sync_run(uuid,uuid,integer,integer,jsonb) is
  'Finalizes an APPLYING sync run through a controlled state transition; client roles cannot update run rows directly.';


create or replace function public.kanban_create_sync_preview(
  p_workspace_id uuid,
  p_board_id uuid,
  p_source_system text,
  p_direction text,
  p_payload_digest text,
  p_preview_plan jsonb
)
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog
as $$
declare
  v_run public.kanban_sync_runs;
  v_item_count integer;
begin
  if auth.uid() is null
     or not kanban_private.has_workspace_role(p_workspace_id, array['owner','admin','editor']) then
    raise exception 'sync_preview_forbidden' using errcode = '42501';
  end if;
  if p_source_system is null
     or p_source_system not in ('pre','hso','notion','github')
     or p_direction is null
     or p_direction not in ('source_to_board','board_to_source','bidirectional') then
    raise exception 'invalid_sync_source_or_direction' using errcode = '22023';
  end if;
  if p_payload_digest is null or p_payload_digest !~ '^[a-f0-9]{64}$' then
    raise exception 'invalid_sync_preview_digest' using errcode = '22023';
  end if;
  if jsonb_typeof(p_preview_plan) is distinct from 'object'
     or jsonb_typeof(p_preview_plan -> 'items') is distinct from 'array'
     or p_preview_plan ->> 'workspace_id' is distinct from p_workspace_id::text
     or p_preview_plan ->> 'board_id' is distinct from p_board_id::text
     or p_preview_plan ->> 'source_system' is distinct from p_source_system
     or p_preview_plan ->> 'direction' is distinct from p_direction then
    raise exception 'sync_preview_plan_scope_mismatch' using errcode = '22023';
  end if;

  v_item_count := jsonb_array_length(p_preview_plan -> 'items');
  if v_item_count < 1 or v_item_count > 100 then
    raise exception 'sync_preview_item_count_out_of_range' using errcode = '22023';
  end if;

  if exists (
    select 1
    from jsonb_array_elements(p_preview_plan -> 'items') as planned(item)
    where jsonb_typeof(planned.item) is distinct from 'object'
       or planned.item ->> 'action' is null
       or planned.item ->> 'action' not in ('CREATE','UPDATE','NOOP','CONFLICT')
       or nullif(trim(planned.item ->> 'source_work_item_id'),'') is null
       or planned.item ->> 'source_digest' is null
       or planned.item ->> 'source_digest' !~ '^[a-f0-9]{64}
  ) then
    raise exception 'sync_preview_item_schema_invalid' using errcode = '22023';
  end if;

  perform 1
  from public.kanban_boards
  where id = p_board_id and workspace_id = p_workspace_id
  for update;
  if not found then
    raise exception 'sync_preview_board_not_found' using errcode = 'P0002';
  end if;

  insert into public.kanban_sync_runs(
    workspace_id,board_id,source_system,direction,status,payload_digest,
    preview_plan,source_count,initiated_by,expires_at
  ) values (
    p_workspace_id,p_board_id,p_source_system,p_direction,'PREVIEWED',
    p_payload_digest,p_preview_plan,v_item_count,auth.uid(),now()+interval '15 minutes'
  )
  returning * into v_run;

  return jsonb_build_object(
    'id',v_run.id,
    'workspace_id',v_run.workspace_id,
    'board_id',v_run.board_id,
    'source_system',v_run.source_system,
    'direction',v_run.direction,
    'status',v_run.status,
    'payload_digest',v_run.payload_digest,
    'source_count',v_run.source_count,
    'expires_at',v_run.expires_at,
    'created_at',v_run.created_at
  );
end;
$$;
revoke all on function public.kanban_create_sync_preview(uuid,uuid,text,text,text,jsonb) from public,anon;
grant execute on function public.kanban_create_sync_preview(uuid,uuid,text,text,text,jsonb) to authenticated;

comment on function public.kanban_create_sync_preview(uuid,uuid,text,text,text,jsonb) is
  'Persists a bounded, workspace-scoped sync preview. Authenticated clients cannot insert sync runs directly.';


create or replace function public.kanban_record_sync_readback(
  p_sync_run_id uuid,
  p_checked_count integer,
  p_issue_count integer
)
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog
as $$
declare
  v_run public.kanban_sync_runs;
  v_disposition text;
begin
  select * into v_run
  from public.kanban_sync_runs
  where id = p_sync_run_id
  for update;

  if not found then
    raise exception 'sync_run_not_found' using errcode = 'P0002';
  end if;
  if auth.uid() is null
     or not kanban_private.has_workspace_role(v_run.workspace_id, array['owner','admin','editor']) then
    raise exception 'sync_read_back_forbidden' using errcode = '42501';
  end if;
  if v_run.status not in ('APPLIED','PARTIAL') then
    raise exception 'sync_run_not_applied' using errcode = '55000';
  end if;
  if p_checked_count is null or p_issue_count is null
     or p_checked_count < 0 or p_issue_count < 0
     or p_issue_count > p_checked_count then
    raise exception 'invalid_sync_read_back_counts' using errcode = '22023';
  end if;

  v_disposition := case when p_issue_count = 0 then 'READ_BACK_PASS' else 'READ_BACK_FAIL' end;

  insert into public.kanban_sync_events(
    workspace_id,sync_run_id,source_system,event_type,disposition,details,actor_user_id
  ) values (
    v_run.workspace_id,v_run.id,v_run.source_system,'READ_BACK',v_disposition,
    jsonb_build_object('checked',p_checked_count,'issue_count',p_issue_count),
    auth.uid()
  );

  return jsonb_build_object(
    'run_id',v_run.id,
    'disposition',v_disposition,
    'checked',p_checked_count,
    'issue_count',p_issue_count
  );
end;
$$;
revoke all on function public.kanban_record_sync_readback(uuid,integer,integer) from public,anon;
grant execute on function public.kanban_record_sync_readback(uuid,integer,integer) to authenticated;

comment on function public.kanban_record_sync_readback(uuid,integer,integer) is
  'Records a bounded read-back result for an applied sync run. Clients cannot insert sync events directly.';

  ) then
    raise exception 'sync_preview_item_schema_invalid' using errcode = '22023';
  end if;

  perform 1
  from public.kanban_boards
  where id = p_board_id and workspace_id = p_workspace_id
  for update;
  if not found then
    raise exception 'sync_preview_board_not_found' using errcode = 'P0002';
  end if;

  insert into public.kanban_sync_runs(
    workspace_id,board_id,source_system,direction,status,payload_digest,
    preview_plan,source_count,initiated_by,expires_at
  ) values (
    p_workspace_id,p_board_id,p_source_system,p_direction,'PREVIEWED',
    p_payload_digest,p_preview_plan,v_item_count,auth.uid(),now()+interval '15 minutes'
  )
  returning * into v_run;

  return jsonb_build_object(
    'id',v_run.id,
    'workspace_id',v_run.workspace_id,
    'board_id',v_run.board_id,
    'source_system',v_run.source_system,
    'direction',v_run.direction,
    'status',v_run.status,
    'payload_digest',v_run.payload_digest,
    'source_count',v_run.source_count,
    'expires_at',v_run.expires_at,
    'created_at',v_run.created_at
  );
end;
$$;
revoke all on function public.kanban_create_sync_preview(uuid,uuid,text,text,text,jsonb) from public,anon;
grant execute on function public.kanban_create_sync_preview(uuid,uuid,text,text,text,jsonb) to authenticated;

comment on function public.kanban_create_sync_preview(uuid,uuid,text,text,text,jsonb) is
  'Persists a bounded, workspace-scoped sync preview. Authenticated clients cannot insert sync runs directly.';


create or replace function public.kanban_record_sync_readback(
  p_sync_run_id uuid,
  p_checked_count integer,
  p_issue_count integer
)
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog
as $$
declare
  v_run public.kanban_sync_runs;
  v_disposition text;
begin
  select * into v_run
  from public.kanban_sync_runs
  where id = p_sync_run_id
  for update;

  if not found then
    raise exception 'sync_run_not_found' using errcode = 'P0002';
  end if;
  if auth.uid() is null
     or not kanban_private.has_workspace_role(v_run.workspace_id, array['owner','admin','editor']) then
    raise exception 'sync_read_back_forbidden' using errcode = '42501';
  end if;
  if v_run.status not in ('APPLIED','PARTIAL') then
    raise exception 'sync_run_not_applied' using errcode = '55000';
  end if;
  if p_checked_count is null or p_issue_count is null
     or p_checked_count < 0 or p_issue_count < 0
     or p_issue_count > p_checked_count then
    raise exception 'invalid_sync_read_back_counts' using errcode = '22023';
  end if;

  v_disposition := case when p_issue_count = 0 then 'READ_BACK_PASS' else 'READ_BACK_FAIL' end;

  insert into public.kanban_sync_events(
    workspace_id,sync_run_id,source_system,event_type,disposition,details,actor_user_id
  ) values (
    v_run.workspace_id,v_run.id,v_run.source_system,'READ_BACK',v_disposition,
    jsonb_build_object('checked',p_checked_count,'issue_count',p_issue_count),
    auth.uid()
  );

  return jsonb_build_object(
    'run_id',v_run.id,
    'disposition',v_disposition,
    'checked',p_checked_count,
    'issue_count',p_issue_count
  );
end;
$$;
revoke all on function public.kanban_record_sync_readback(uuid,integer,integer) from public,anon;
grant execute on function public.kanban_record_sync_readback(uuid,integer,integer) to authenticated;

comment on function public.kanban_record_sync_readback(uuid,integer,integer) is
  'Records a bounded read-back result for an applied sync run. Clients cannot insert sync events directly.';
