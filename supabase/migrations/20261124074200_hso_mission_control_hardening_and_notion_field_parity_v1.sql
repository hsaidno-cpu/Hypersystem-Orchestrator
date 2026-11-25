-- HSO Mission Control hardening and Notion field parity.
revoke all on table public.hso_members from anon;
grant select on table public.hso_members to authenticated;

revoke all on table public.hso_integration_events from anon, authenticated;
grant all on table public.hso_integration_events to service_role;

drop policy if exists hso_integration_events_service_role_all on public.hso_integration_events;
create policy hso_integration_events_service_role_all
  on public.hso_integration_events
  for all
  to service_role
  using (true)
  with check (true);

alter table public.hso_work_items
  add column if not exists project_area text,
  add column if not exists record_type text,
  add column if not exists acceptance_criteria text,
  add column if not exists progress_percent numeric(5,2),
  add column if not exists progress_basis text,
  add column if not exists source_commit text,
  add column if not exists target_date date;

alter table public.hso_executions
  add column if not exists execution_id text,
  add column if not exists run_type text,
  add column if not exists source_commit text,
  add column if not exists source_repository text,
  add column if not exists plan_artifact_url text,
  add column if not exists supporting_evidence jsonb not null default '[]'::jsonb,
  add column if not exists supporting_specialists jsonb not null default '[]'::jsonb,
  add column if not exists verification_state text;

alter table public.hso_evidence_records
  add column if not exists evidence_id text,
  add column if not exists content_digest text,
  add column if not exists source_locator text,
  add column if not exists verified_at timestamptz,
  add column if not exists verifier_role text,
  add column if not exists related_work_item text;
