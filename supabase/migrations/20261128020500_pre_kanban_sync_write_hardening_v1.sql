-- Restrict synchronization state mutations to the reviewed transactional RPCs.
drop policy if exists kanban_sync_runs_update on public.kanban_sync_runs;
revoke insert,update,delete on public.kanban_sync_runs from authenticated;

drop policy if exists kanban_sync_events_insert on public.kanban_sync_events;
revoke insert,update,delete on public.kanban_sync_events from authenticated;

drop policy if exists kanban_sync_bindings_insert on public.kanban_sync_bindings;
drop policy if exists kanban_sync_bindings_update on public.kanban_sync_bindings;
revoke insert,update,delete on public.kanban_sync_bindings from authenticated;

-- Sync runs remain readable and can be created by the preview operation.
-- State transitions are only available through kanban_claim_sync_run and kanban_finalize_sync_run.
-- Bindings are created/advanced only through kanban_apply_sync_item and kanban_ack_sync_outbox.
comment on table public.kanban_sync_runs is
  'Sync lifecycle state. Authenticated clients cannot update rows directly; transitions use controlled RPCs.';
comment on table public.kanban_sync_bindings is
  'Source-to-card binding. Authenticated clients have read-only access; sync RPCs own binding changes.';
