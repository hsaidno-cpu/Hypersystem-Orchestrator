-- HSO Mission Control allowlisted access model.
create table if not exists public.hso_members (
 user_id uuid primary key references auth.users(id) on delete cascade,
 role text not null check(role in ('admin','operator','reviewer','observer')),
 active boolean not null default true, created_at timestamptz not null default now(), created_by text
);
alter table public.hso_members enable row level security;
alter table public.hso_members force row level security;
grant select on public.hso_members to authenticated;
grant select on public.hso_sources,public.hso_sync_runs,public.hso_source_snapshots,public.hso_work_items,public.hso_executions,public.hso_evidence_records,public.hso_decisions,public.hso_prompt_artifacts,public.hso_notifications to authenticated;
create policy hso_members_select_self on public.hso_members for select to authenticated using(user_id=(select auth.uid()));
create policy hso_sources_select_member on public.hso_sources for select to authenticated using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
create policy hso_sync_runs_select_member on public.hso_sync_runs for select to authenticated using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
create policy hso_source_snapshots_select_member on public.hso_source_snapshots for select to authenticated using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
create policy hso_work_items_select_member on public.hso_work_items for select to authenticated using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
create policy hso_executions_select_member on public.hso_executions for select to authenticated using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
create policy hso_evidence_records_select_member on public.hso_evidence_records for select to authenticated using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
create policy hso_decisions_select_member on public.hso_decisions for select to authenticated using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
create policy hso_prompt_artifacts_select_member on public.hso_prompt_artifacts for select to authenticated using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
create policy hso_notifications_select_member on public.hso_notifications for select to authenticated using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
revoke insert,update,delete on public.hso_members from anon,authenticated;
revoke insert,update,delete on public.hso_sources,public.hso_sync_runs,public.hso_integration_events,public.hso_source_snapshots,public.hso_work_items,public.hso_executions,public.hso_evidence_records,public.hso_decisions,public.hso_prompt_artifacts,public.hso_notifications from anon,authenticated;
