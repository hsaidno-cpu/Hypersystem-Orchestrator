-- HSO Mission Control work-item transition history and milestone identifiers.
alter table public.hso_work_items add column if not exists parent_milestone_id text;
alter table public.hso_progress_snapshots
  add column if not exists milestone_title text,
  add column if not exists group_type text not null default 'ECOSYSTEM_STAGE'
    check(group_type in ('GLOBAL','MILESTONE','ECOSYSTEM_STAGE'));
alter table public.hso_executions
  add column if not exists executing_agent text,
  add column if not exists target_branch text,
  add column if not exists head_commit_sha text,
  add column if not exists changed_files jsonb not null default '[]'::jsonb,
  add column if not exists validation_summary text,
  add column if not exists acceptance_result text,
  add column if not exists stop_reason text;

create table if not exists public.hso_work_item_history (
  id uuid primary key default gen_random_uuid(),
  work_item_id uuid not null references public.hso_work_items(id) on delete cascade,
  source_key text not null references public.hso_sources(source_key),
  external_id text not null,
  transition_key text not null unique,
  from_execution_state text,
  to_execution_state text,
  from_gate_state text,
  to_gate_state text,
  from_verification_state text,
  to_verification_state text,
  changed_at timestamptz not null default now(),
  source_updated_at timestamptz,
  source_url text,
  changed_fields jsonb not null default '[]'::jsonb,
  observed_payload jsonb not null default '{}'::jsonb
);
create index if not exists hso_work_item_history_work_item_idx on public.hso_work_item_history(work_item_id,changed_at desc);
create index if not exists hso_work_item_history_source_idx on public.hso_work_item_history(source_key,external_id,changed_at desc);
alter table public.hso_work_item_history enable row level security;
alter table public.hso_work_item_history force row level security;
revoke all on public.hso_work_item_history from anon,authenticated;
grant select on public.hso_work_item_history to authenticated;
grant all on public.hso_work_item_history to service_role;
drop policy if exists hso_work_item_history_member_read on public.hso_work_item_history;
create policy hso_work_item_history_member_read on public.hso_work_item_history for select to authenticated
 using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
grant select on public.hso_verified_work_items_v to authenticated;
