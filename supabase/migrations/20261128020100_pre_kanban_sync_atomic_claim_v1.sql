-- Atomic PRE/HSO sync application and recoverable run claim.
alter table public.kanban_sync_runs
  add column if not exists claimed_at timestamptz;

create or replace function public.kanban_claim_sync_run(
  p_sync_run_id uuid,
  p_expected_digest text
)
returns jsonb
language plpgsql
security invoker
set search_path = pg_catalog,public,kanban_private,auth
as $$
declare
  v_run public.kanban_sync_runs;
begin
  select * into v_run
  from public.kanban_sync_runs
  where id=p_sync_run_id
  for update;

  if not found then
    raise exception 'sync_run_not_found' using errcode='P0002';
  end if;
  if not kanban_private.has_workspace_role(v_run.workspace_id,array['owner','admin','editor']) then
    raise exception 'sync_run_write_forbidden' using errcode='42501';
  end if;
  if v_run.payload_digest <> p_expected_digest then
    raise exception 'preview_digest_mismatch' using errcode='22023';
  end if;
  if v_run.status='APPLYING' and v_run.claimed_at < now()-interval '5 minutes' then
    update public.kanban_sync_runs set claimed_at=now() where id=v_run.id;
    return jsonb_build_object('status','APPLYING','sync_run_id',v_run.id,'reclaimed',true);
  end if;
  if v_run.status='PARTIAL'
     and coalesce((v_run.result_summary->>'failed')::integer,0)>0
     and (v_run.claimed_at is null or v_run.claimed_at < now()-interval '5 minutes') then
    update public.kanban_sync_runs set status='APPLYING',claimed_at=now() where id=v_run.id;
    return jsonb_build_object('status','APPLYING','sync_run_id',v_run.id,'reclaimed',true,'retry',true);
  end if;
  if v_run.status <> 'PREVIEWED' then
    raise exception 'sync_run_not_claimable:%',v_run.status using errcode='55000';
  end if;
  if v_run.expires_at <= now() then
    update public.kanban_sync_runs set status='EXPIRED' where id=v_run.id;
    return jsonb_build_object('status','EXPIRED','sync_run_id',v_run.id);
  end if;

  update public.kanban_sync_runs set status='APPLYING',claimed_at=now()
  where id=v_run.id and status='PREVIEWED';
  return jsonb_build_object('status','APPLYING','sync_run_id',v_run.id,'reclaimed',false);
end;
$$;
revoke all on function public.kanban_claim_sync_run(uuid,text) from public,anon;
grant execute on function public.kanban_claim_sync_run(uuid,text) to authenticated;

create or replace function public.kanban_apply_sync_item(
  p_sync_run_id uuid,
  p_item_payload jsonb
)
returns jsonb
language plpgsql
security invoker
set search_path = pg_catalog,public,kanban_private,auth
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
  where id=p_sync_run_id
  for share;
  if not found then raise exception 'sync_run_not_found' using errcode='P0002'; end if;
  if v_run.status <> 'APPLYING' then raise exception 'sync_run_not_applying' using errcode='55000'; end if;
  if not kanban_private.has_workspace_role(v_run.workspace_id,array['owner','admin','editor']) then
    raise exception 'sync_item_write_forbidden' using errcode='42501';
  end if;

  v_action=p_item_payload->>'action';
  v_source_id=p_item_payload->>'source_work_item_id';
  v_digest=p_item_payload->>'source_digest';
  if v_source_id is null or v_digest is null or v_digest !~ '^[a-f0-9]{64}
    raise exception 'invalid_sync_item_identity_or_digest' using errcode='22023';
  end if;

  if v_action='CREATE' then
    select * into v_binding from public.kanban_sync_bindings
    where workspace_id=v_run.workspace_id and source_system=v_run.source_system
      and source_work_item_id=v_source_id
    for update;

    if found then
      if v_binding.last_source_digest=v_digest then
        return jsonb_build_object('disposition','NOOP','card_id',v_binding.card_id,'source_work_item_id',v_source_id);
      end if;
      return jsonb_build_object('disposition','CONFLICT','reason','source_binding_already_exists_with_different_digest','card_id',v_binding.card_id);
    end if;

    v_column_id=(p_item_payload->>'column_id')::uuid;
    if not exists (
      select 1 from public.kanban_columns
      where id=v_column_id and board_id=v_run.board_id and workspace_id=v_run.workspace_id and not is_archived
    ) then
      return jsonb_build_object('disposition','CONFLICT','reason','target_column_missing_or_outside_board');
    end if;

    select coalesce(max(position),0)+1000 into v_position
    from public.kanban_cards
    where board_id=v_run.board_id and column_id=v_column_id and not is_archived;

    v_metadata=jsonb_build_object(
      'source_system',v_run.source_system,
      'evidence_refs',coalesce(p_item_payload->'evidence_refs','[]'::jsonb),
      'dependencies',coalesce(p_item_payload->'dependencies','[]'::jsonb)
    ) || coalesce(p_item_payload->'extra','{}'::jsonb);

    insert into public.kanban_cards(
      workspace_id,board_id,column_id,title,description,priority,
      acceptance_criteria,position,metadata,created_by,updated_by
    ) values (
      v_run.workspace_id,v_run.board_id,v_column_id,p_item_payload->>'title',
      p_item_payload->>'description',coalesce(p_item_payload->>'priority','medium'),
      p_item_payload->>'acceptance_criteria',v_position,v_metadata,auth.uid(),auth.uid()
    ) returning * into v_card;

    insert into public.kanban_sync_bindings(
      workspace_id,board_id,card_id,source_system,source_work_item_id,source_revision,
      last_source_digest,last_board_revision,sync_direction
    ) values (
      v_run.workspace_id,v_run.board_id,v_card.id,v_run.source_system,v_source_id,
      p_item_payload->>'source_revision',v_digest,v_card.revision,v_run.direction
    );
    v_disposition='CREATED';

  elsif v_action='UPDATE' then
    select * into v_binding from public.kanban_sync_bindings
    where workspace_id=v_run.workspace_id and source_system=v_run.source_system
      and source_work_item_id=v_source_id
    for update;
    if not found then
      return jsonb_build_object('disposition','CONFLICT','reason','source_binding_missing');
    end if;

    select * into v_card from public.kanban_cards
    where id=v_binding.card_id and board_id=v_run.board_id
    for update;
    if not found or v_card.is_archived then
      return jsonb_build_object('disposition','CONFLICT','reason','bound_card_missing_or_archived');
    end if;

    v_expected_revision=(p_item_payload->>'expected_revision')::integer;
    if v_binding.last_source_digest=v_digest then
      return jsonb_build_object('disposition','NOOP','card_id',v_card.id,'card_revision',v_card.revision,'source_work_item_id',v_source_id);
    end if;
    if v_card.revision<>v_expected_revision or v_binding.last_board_revision<>v_expected_revision then
      return jsonb_build_object(
        'disposition','CONFLICT','reason','board_card_revision_changed',
        'expected_revision',v_expected_revision,'actual_revision',v_card.revision
      );
    end if;

    v_column_id=(p_item_payload->>'column_id')::uuid;
    if not exists (
      select 1 from public.kanban_columns
      where id=v_column_id and board_id=v_run.board_id and workspace_id=v_run.workspace_id and not is_archived
    ) then
      return jsonb_build_object('disposition','CONFLICT','reason','target_column_missing_or_outside_board');
    end if;

    perform set_config('kanban.suppress_outbox','on',true);
    v_metadata=jsonb_build_object(
      'source_system',v_run.source_system,
      'evidence_refs',coalesce(p_item_payload->'evidence_refs','[]'::jsonb),
      'dependencies',coalesce(p_item_payload->'dependencies','[]'::jsonb)
    ) || coalesce(p_item_payload->'extra','{}'::jsonb);

    update public.kanban_cards set
      column_id=v_column_id,title=p_item_payload->>'title',
      description=p_item_payload->>'description',
      priority=coalesce(p_item_payload->>'priority','medium'),
      acceptance_criteria=p_item_payload->>'acceptance_criteria',
      metadata=v_metadata,updated_by=auth.uid()
    where id=v_card.id
    returning * into v_card;

    update public.kanban_sync_bindings set
      source_revision=p_item_payload->>'source_revision',
      last_source_digest=v_digest,
      last_board_revision=v_card.revision,
      last_synced_at=now()
    where id=v_binding.id;
    v_disposition='UPDATED';
  else
    raise exception 'unsupported_sync_action:%',v_action using errcode='22023';
  end if;

  insert into public.kanban_sync_events(
    workspace_id,sync_run_id,source_system,source_work_item_id,event_type,disposition,
    details,actor_user_id
  ) values (
    v_run.workspace_id,v_run.id,v_run.source_system,v_source_id,v_action,v_disposition,
    jsonb_build_object('card_id',v_card.id,'card_revision',v_card.revision,'source_digest',v_digest),
    auth.uid()
  );

  return jsonb_build_object(
    'disposition',v_disposition,'card_id',v_card.id,'card_revision',v_card.revision,
    'source_work_item_id',v_source_id
  );
end;
$$;
revoke all on function public.kanban_apply_sync_item(uuid,jsonb) from public,anon;
grant execute on function public.kanban_apply_sync_item(uuid,jsonb) to authenticated;

comment on function public.kanban_apply_sync_item(uuid,jsonb) is
  'Applies one sync item and its binding/event in a single Postgres transaction; safe to replay after worker interruption.';
 then
    raise exception 'invalid_sync_item_identity_or_digest' using errcode='22023';
  end if;

  if v_action='CREATE' then
    select * into v_binding from public.kanban_sync_bindings
    where workspace_id=v_run.workspace_id and source_system=v_run.source_system
      and source_work_item_id=v_source_id
    for update;

    if found then
      if v_binding.last_source_digest=v_digest then
        return jsonb_build_object('disposition','NOOP','card_id',v_binding.card_id,'source_work_item_id',v_source_id);
      end if;
      return jsonb_build_object('disposition','CONFLICT','reason','source_binding_already_exists_with_different_digest','card_id',v_binding.card_id);
    end if;

    v_column_id=(p_item_payload->>'column_id')::uuid;
    if not exists (
      select 1 from public.kanban_columns
      where id=v_column_id and board_id=v_run.board_id and workspace_id=v_run.workspace_id and not is_archived
    ) then
      return jsonb_build_object('disposition','CONFLICT','reason','target_column_missing_or_outside_board');
    end if;

    select coalesce(max(position),0)+1000 into v_position
    from public.kanban_cards
    where board_id=v_run.board_id and column_id=v_column_id and not is_archived;

    v_metadata=jsonb_build_object(
      'source_system',v_run.source_system,
      'evidence_refs',coalesce(p_item_payload->'evidence_refs','[]'::jsonb),
      'dependencies',coalesce(p_item_payload->'dependencies','[]'::jsonb)
    ) || coalesce(p_item_payload->'extra','{}'::jsonb);

    insert into public.kanban_cards(
      workspace_id,board_id,column_id,title,description,priority,
      acceptance_criteria,position,metadata,created_by,updated_by
    ) values (
      v_run.workspace_id,v_run.board_id,v_column_id,p_item_payload->>'title',
      p_item_payload->>'description',coalesce(p_item_payload->>'priority','medium'),
      p_item_payload->>'acceptance_criteria',v_position,v_metadata,auth.uid(),auth.uid()
    ) returning * into v_card;

    insert into public.kanban_sync_bindings(
      workspace_id,board_id,card_id,source_system,source_work_item_id,source_revision,
      last_source_digest,last_board_revision,sync_direction
    ) values (
      v_run.workspace_id,v_run.board_id,v_card.id,v_run.source_system,v_source_id,
      p_item_payload->>'source_revision',v_digest,v_card.revision,v_run.direction
    );
    v_disposition='CREATED';

  elsif v_action='UPDATE' then
    select * into v_binding from public.kanban_sync_bindings
    where workspace_id=v_run.workspace_id and source_system=v_run.source_system
      and source_work_item_id=v_source_id
    for update;
    if not found then
      return jsonb_build_object('disposition','CONFLICT','reason','source_binding_missing');
    end if;

    select * into v_card from public.kanban_cards
    where id=v_binding.card_id and board_id=v_run.board_id
    for update;
    if not found or v_card.is_archived then
      return jsonb_build_object('disposition','CONFLICT','reason','bound_card_missing_or_archived');
    end if;

    v_expected_revision=(p_item_payload->>'expected_revision')::integer;
    if v_binding.last_source_digest=v_digest then
      return jsonb_build_object('disposition','NOOP','card_id',v_card.id,'card_revision',v_card.revision,'source_work_item_id',v_source_id);
    end if;
    if v_card.revision<>v_expected_revision or v_binding.last_board_revision<>v_expected_revision then
      return jsonb_build_object(
        'disposition','CONFLICT','reason','board_card_revision_changed',
        'expected_revision',v_expected_revision,'actual_revision',v_card.revision
      );
    end if;

    v_column_id=(p_item_payload->>'column_id')::uuid;
    if not exists (
      select 1 from public.kanban_columns
      where id=v_column_id and board_id=v_run.board_id and workspace_id=v_run.workspace_id and not is_archived
    ) then
      return jsonb_build_object('disposition','CONFLICT','reason','target_column_missing_or_outside_board');
    end if;

    perform set_config('kanban.suppress_outbox','on',true);
    v_metadata=jsonb_build_object(
      'source_system',v_run.source_system,
      'evidence_refs',coalesce(p_item_payload->'evidence_refs','[]'::jsonb),
      'dependencies',coalesce(p_item_payload->'dependencies','[]'::jsonb)
    ) || coalesce(p_item_payload->'extra','{}'::jsonb);

    update public.kanban_cards set
      column_id=v_column_id,title=p_item_payload->>'title',
      description=p_item_payload->>'description',
      priority=coalesce(p_item_payload->>'priority','medium'),
      acceptance_criteria=p_item_payload->>'acceptance_criteria',
      metadata=v_metadata,updated_by=auth.uid()
    where id=v_card.id
    returning * into v_card;

    update public.kanban_sync_bindings set
      source_revision=p_item_payload->>'source_revision',
      last_source_digest=v_digest,
      last_board_revision=v_card.revision,
      last_synced_at=now()
    where id=v_binding.id;
    v_disposition='UPDATED';
  else
    raise exception 'unsupported_sync_action:%',v_action using errcode='22023';
  end if;

  insert into public.kanban_sync_events(
    workspace_id,sync_run_id,source_system,source_work_item_id,event_type,disposition,
    details,actor_user_id
  ) values (
    v_run.workspace_id,v_run.id,v_run.source_system,v_source_id,v_action,v_disposition,
    jsonb_build_object('card_id',v_card.id,'card_revision',v_card.revision,'source_digest',v_digest),
    auth.uid()
  );

  return jsonb_build_object(
    'disposition',v_disposition,'card_id',v_card.id,'card_revision',v_card.revision,
    'source_work_item_id',v_source_id
  );
end;
$$;
revoke all on function public.kanban_apply_sync_item(uuid,jsonb) from public,anon;
grant execute on function public.kanban_apply_sync_item(uuid,jsonb) to authenticated;

comment on function public.kanban_apply_sync_item(uuid,jsonb) is
  'Applies one sync item and its binding/event in a single Postgres transaction; safe to replay after worker interruption.';
