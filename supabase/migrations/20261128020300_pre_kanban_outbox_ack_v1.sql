-- Atomic acknowledgment of outbound PRE/HSO changes.
create or replace function public.kanban_ack_sync_outbox(
  p_outbox_id uuid,
  p_expected_card_revision integer,
  p_resulting_source_revision text,
  p_source_readback_ref text,
  p_source_readback_digest text
)
returns jsonb
language plpgsql
security invoker
set search_path = pg_catalog,public,kanban_private,auth
as $$
declare
  v_item public.kanban_sync_outbox;
  v_affected integer;
begin
  select * into v_item
  from public.kanban_sync_outbox
  where id=p_outbox_id
  for update;

  if not found then raise exception 'outbox_item_not_found' using errcode='P0002'; end if;
  if not kanban_private.has_workspace_role(v_item.workspace_id,array['owner','admin','editor']) then
    raise exception 'outbox_acknowledge_forbidden' using errcode='42501';
  end if;
  if v_item.status<>'PENDING' then raise exception 'outbox_item_not_pending' using errcode='55000'; end if;
  if v_item.card_revision<>p_expected_card_revision then
    raise exception 'outbox_card_revision_mismatch' using errcode='22023';
  end if;
  if p_resulting_source_revision is null or length(trim(p_resulting_source_revision))=0 then
    raise exception 'resulting_source_revision_required' using errcode='22023';
  end if;
  if p_source_readback_ref is null or p_source_readback_ref !~ '^https://' then raise exception 'https_readback_reference_required' using errcode='22023'; end if;
  if p_source_readback_digest is null or p_source_readback_digest !~ '^[a-f0-9]{64} raise exception 'sha256_readback_digest_required' using errcode='22023'; end if;

  update public.kanban_sync_outbox set
    status='ACKNOWLEDGED',
    acknowledged_source_revision=p_resulting_source_revision,
    acknowledgement_ref=p_source_readback_ref,
    acknowledgement_digest=p_source_readback_digest,
    acknowledged_by=auth.uid(),
    acknowledged_at=now()
  where id=v_item.id and status='PENDING';
  get diagnostics v_affected=row_count;
  if v_affected<>1 then raise exception 'outbox_acknowledge_race' using errcode='40001'; end if;

  update public.kanban_sync_bindings set
    source_revision=p_resulting_source_revision,
    last_board_revision=v_item.card_revision,
    last_synced_at=now()
  where workspace_id=v_item.workspace_id and board_id=v_item.board_id
    and card_id=v_item.card_id and source_system=v_item.source_system
    and source_work_item_id=v_item.source_work_item_id;
  get diagnostics v_affected=row_count;
  if v_affected<>1 then raise exception 'sync_binding_missing_for_outbox_ack' using errcode='P0002'; end if;

  return jsonb_build_object(
    'acknowledged',true,'outbox_id',v_item.id,
    'source_system',v_item.source_system,
    'source_work_item_id',v_item.source_work_item_id,
    'resulting_source_revision',p_resulting_source_revision,
    'source_readback_ref',p_source_readback_ref,
    'source_readback_digest',p_source_readback_digest,
    'attestation_boundary','RECEIPT_REFERENCE_RECORDED_NOT_INDEPENDENTLY_VERIFIED'
  );
end;
$$;
revoke all on function public.kanban_ack_sync_outbox(uuid,integer,text,text,text) from public,anon;
grant execute on function public.kanban_ack_sync_outbox(uuid,integer,text,text,text) to authenticated;

drop trigger if exists kanban_sync_outbox_audit_after_change on public.kanban_sync_outbox;
create trigger kanban_sync_outbox_audit_after_change
after insert or update or delete on public.kanban_sync_outbox
for each row execute function kanban_private.audit_change();

comment on function public.kanban_ack_sync_outbox(uuid,integer,text,text,text) is
  'Atomically records adapter acknowledgment and advances the PRE/HSO source revision binding after adapter read-back.';
 then raise exception 'sha256_readback_digest_required' using errcode='22023'; end if;

  update public.kanban_sync_outbox set
    status='ACKNOWLEDGED',
    acknowledged_source_revision=p_resulting_source_revision,
    acknowledgement_ref=p_source_readback_ref,
    acknowledgement_digest=p_source_readback_digest,
    acknowledged_by=auth.uid(),
    acknowledged_at=now()
  where id=v_item.id and status='PENDING';

  update public.kanban_sync_bindings set
    source_revision=p_resulting_source_revision,
    last_board_revision=v_item.card_revision,
    last_synced_at=now()
  where workspace_id=v_item.workspace_id and board_id=v_item.board_id
    and card_id=v_item.card_id and source_system=v_item.source_system
    and source_work_item_id=v_item.source_work_item_id;

  return jsonb_build_object(
    'acknowledged',true,'outbox_id',v_item.id,
    'source_system',v_item.source_system,
    'source_work_item_id',v_item.source_work_item_id,
    'resulting_source_revision',p_resulting_source_revision,
    'source_readback_ref',p_source_readback_ref,
    'source_readback_digest',p_source_readback_digest,
    'attestation_boundary','RECEIPT_REFERENCE_RECORDED_NOT_INDEPENDENTLY_VERIFIED'
  );
end;
$$;
revoke all on function public.kanban_ack_sync_outbox(uuid,integer,text,text,text) from public,anon;
grant execute on function public.kanban_ack_sync_outbox(uuid,integer,text,text,text) to authenticated;

drop trigger if exists kanban_sync_outbox_audit_after_change on public.kanban_sync_outbox;
create trigger kanban_sync_outbox_audit_after_change
after insert or update or delete on public.kanban_sync_outbox
for each row execute function kanban_private.audit_change();

comment on function public.kanban_ack_sync_outbox(uuid,integer,text,text,text) is
  'Atomically records adapter acknowledgment and advances the PRE/HSO source revision binding after adapter read-back.';
