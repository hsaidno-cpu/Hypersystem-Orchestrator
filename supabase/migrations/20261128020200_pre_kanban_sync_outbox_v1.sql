-- PRE Kanban outbound change outbox v1.
-- Board-originated edits are persisted for a trusted PRE/HSO adapter to consume.
create table if not exists public.kanban_sync_outbox (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  board_id uuid not null,
  card_id uuid not null,
  source_system text not null check (source_system in ('pre','hso','notion','github')),
  source_work_item_id text not null,
  source_revision text,
  card_revision integer not null check (card_revision > 0),
  idempotency_key text not null unique,
  payload jsonb not null,
  status text not null default 'PENDING'
    check (status in ('PENDING','ACKNOWLEDGED','CONFLICT','DEAD_LETTER')),
  attempts integer not null default 0 check (attempts >= 0),
  last_error text,
  acknowledged_source_revision text,
  acknowledgement_ref text,
  acknowledgement_digest text,
  acknowledged_by uuid references auth.users(id) on delete set null,
  acknowledged_at timestamptz,
  created_at timestamptz not null default now(),
  foreign key (workspace_id,board_id) references public.kanban_boards(workspace_id,id) on delete cascade,
  foreign key (board_id,card_id) references public.kanban_cards(board_id,id) on delete cascade
);
create index if not exists kanban_sync_outbox_pending_idx
  on public.kanban_sync_outbox(workspace_id,status,created_at);

alter table public.kanban_sync_outbox enable row level security;
create policy kanban_sync_outbox_select on public.kanban_sync_outbox
for select to authenticated using (
  kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor'])
);
create policy kanban_sync_outbox_update on public.kanban_sync_outbox
for update to authenticated using (
  kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor'])
) with check (
  kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor'])
);
grant select,update on public.kanban_sync_outbox to authenticated;
revoke all on public.kanban_sync_outbox from anon;

create or replace function kanban_private.capture_card_change_outbox()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog,public,kanban_private,auth
as $$
declare
  v_binding record;
  v_payload jsonb;
  v_idempotency_key text;
begin
  if tg_op <> 'UPDATE' or new.revision = old.revision
     or current_setting('kanban.suppress_outbox',true)='on' then
    return new;
  end if;

  for v_binding in
    select id,workspace_id,board_id,source_system,source_work_item_id,source_revision,sync_direction
    from public.kanban_sync_bindings
    where card_id=new.id and sync_direction in ('board_to_source','bidirectional')
  loop
    v_payload := jsonb_build_object(
      'source_system',v_binding.source_system,
      'source_work_item_id',v_binding.source_work_item_id,
      'source_revision',v_binding.source_revision,
      'card_id',new.id,
      'card_revision',new.revision,
      'title',new.title,
      'description',new.description,
      'priority',new.priority,
      'acceptance_criteria',new.acceptance_criteria,
      'due_date',new.due_date,
      'column_id',new.column_id,
      'metadata',new.metadata,
      'changed_at',new.updated_at
    );
    v_idempotency_key := new.id::text || ':' || new.revision::text || ':' || v_binding.source_system;
    insert into public.kanban_sync_outbox(
      workspace_id,board_id,card_id,source_system,source_work_item_id,source_revision,
      card_revision,idempotency_key,payload,status
    ) values (
      v_binding.workspace_id,v_binding.board_id,new.id,v_binding.source_system,
      v_binding.source_work_item_id,v_binding.source_revision,new.revision,
      v_idempotency_key,v_payload,'PENDING'
    ) on conflict (idempotency_key) do nothing;
  end loop;
  return new;
end;
$$;
revoke all on function kanban_private.capture_card_change_outbox() from public,anon,authenticated;

drop trigger if exists kanban_card_change_outbox_after_update on public.kanban_cards;
create trigger kanban_card_change_outbox_after_update
after update on public.kanban_cards
for each row execute function kanban_private.capture_card_change_outbox();

comment on table public.kanban_sync_outbox is
  'Persistent outbound change queue for PRE/HSO adapters. ACKNOWLEDGED is an adapter-provided read-back assertion, not a cryptographically verified source receipt.';
