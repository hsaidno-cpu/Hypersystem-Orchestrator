-- HSO Mission Control intelligence schema v2.
alter table public.hso_work_items
  add column if not exists milestone_key text,
  add column if not exists scope_weight numeric(12,2),
  add column if not exists weight_rationale text,
  add column if not exists estimated_effort_hours numeric(12,2),
  add column if not exists dependency_unlock_value numeric(5,2),
  add column if not exists risk_reduction numeric(5,2),
  add column if not exists critical_path_impact numeric(5,2),
  add column if not exists urgency numeric(5,2),
  add column if not exists effort_efficiency numeric(5,2),
  add column if not exists evidence_confidence numeric(5,2),
  add column if not exists requires_human_approval boolean,
  add column if not exists approval_state text,
  add column if not exists security_disposition text,
  add column if not exists execution_risk text,
  add column if not exists target_branch text,
  add column if not exists head_commit_sha text,
  add column if not exists reviewed_commit_sha text,
  add column if not exists ci_commit_sha text,
  add column if not exists dependency_work_item_ids jsonb not null default '[]'::jsonb,
  add column if not exists change_surface text,
  add column if not exists execution_target text,
  add column if not exists source_verified_at timestamptz;

do $$
begin
  if not exists(select 1 from pg_constraint where conname='hso_work_items_scope_weight_positive') then
    alter table public.hso_work_items add constraint hso_work_items_scope_weight_positive check(scope_weight is null or scope_weight>0);
  end if;
  if not exists(select 1 from pg_constraint where conname='hso_work_items_score_ranges') then
    alter table public.hso_work_items add constraint hso_work_items_score_ranges check(
      (dependency_unlock_value is null or dependency_unlock_value between 0 and 100) and
      (risk_reduction is null or risk_reduction between 0 and 100) and
      (critical_path_impact is null or critical_path_impact between 0 and 100) and
      (urgency is null or urgency between 0 and 100) and
      (effort_efficiency is null or effort_efficiency between 0 and 100) and
      (evidence_confidence is null or evidence_confidence between 0 and 100));
  end if;
  if not exists(select 1 from pg_constraint where conname='hso_work_items_approval_state_check') then
    alter table public.hso_work_items add constraint hso_work_items_approval_state_check check(approval_state is null or approval_state in ('NOT_REQUIRED','PENDING','APPROVED','REJECTED'));
  end if;
  if not exists(select 1 from pg_constraint where conname='hso_work_items_security_disposition_check') then
    alter table public.hso_work_items add constraint hso_work_items_security_disposition_check check(security_disposition is null or security_disposition in ('NOT_REQUIRED','PENDING','PASS','HOLD','FAIL'));
  end if;
  if not exists(select 1 from pg_constraint where conname='hso_work_items_execution_risk_check') then
    alter table public.hso_work_items add constraint hso_work_items_execution_risk_check check(execution_risk is null or execution_risk in ('LOW','MEDIUM','HIGH','CRITICAL'));
  end if;
end $$;

create index if not exists hso_work_items_milestone_idx on public.hso_work_items(milestone_key,execution_state,gate_state);
create index if not exists hso_work_items_head_sha_idx on public.hso_work_items(head_commit_sha);

create table if not exists public.hso_progress_snapshots (
  id uuid primary key default gen_random_uuid(),
  project_key text not null default 'hso',
  milestone_key text,
  total_work_items integer not null default 0,
  weighted_work_items integer not null default 0,
  unweighted_work_items integer not null default 0,
  scope_weight_total numeric(14,2) not null default 0,
  verified_weight numeric(14,2) not null default 0,
  weighted_progress_pct numeric(7,2),
  weight_coverage_pct numeric(7,2),
  verified_count integer not null default 0,
  active_count integer not null default 0,
  blocked_count integer not null default 0,
  failed_count integer not null default 0,
  pending_approval_count integer not null default 0,
  measurement_state text not null default 'UNMEASURED'
    check(measurement_state in ('MEASURED','PARTIAL_COVERAGE','UNMEASURED')),
  methodology_version text not null default 'weighted-evidence-v1',
  computed_at timestamptz not null default now()
);
create index if not exists hso_progress_snapshots_project_time_idx on public.hso_progress_snapshots(project_key,computed_at desc);
create index if not exists hso_progress_snapshots_milestone_time_idx on public.hso_progress_snapshots(milestone_key,computed_at desc);

create table if not exists public.hso_decision_runs (
  id uuid primary key default gen_random_uuid(),
  engine_version text not null,
  policy_version text not null,
  decision_state text not null check(decision_state in ('PRIMARY_SELECTED','NO_ELIGIBLE_ACTION','SOURCE_STALE','SOURCE_CONFLICT')),
  primary_work_item_id uuid references public.hso_work_items(id) on delete set null,
  source_health jsonb not null default '{}'::jsonb,
  primary_action jsonb,
  supporting_actions jsonb not null default '[]'::jsonb,
  blocked_actions jsonb not null default '[]'::jsonb,
  pending_decisions jsonb not null default '[]'::jsonb,
  ranking_snapshot jsonb not null default '[]'::jsonb,
  completion_gap jsonb not null default '{}'::jsonb,
  prompt_artifact_id uuid,
  computed_at timestamptz not null default now()
);
create index if not exists hso_decision_runs_latest_idx on public.hso_decision_runs(computed_at desc);

create table if not exists public.hso_issue_records (
  id uuid primary key default gen_random_uuid(),
  source_key text references public.hso_sources(source_key),
  external_id text,
  root_cause_key text not null,
  issue_type text not null,
  severity text not null check(severity in ('CRITICAL','HIGH','MEDIUM','LOW','INFO')),
  detected_at timestamptz not null default now(),
  location text,
  root_cause text,
  root_cause_state text not null default 'UNCONFIRMED' check(root_cause_state in ('UNCONFIRMED','CONFIRMED','DISPUTED')),
  impact text,
  affected_work_items jsonb not null default '[]'::jsonb,
  affected_milestones jsonb not null default '[]'::jsonb,
  resolution text,
  verification_state text not null default 'OPEN' check(verification_state in ('OPEN','IN_PROGRESS','VERIFIED','REOPENED')),
  verification_evidence_url text,
  first_seen_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(),
  occurrence_count integer not null default 1,
  unique(source_key,external_id)
);
create index if not exists hso_issue_records_root_cause_idx on public.hso_issue_records(root_cause_key,severity);
create index if not exists hso_issue_records_severity_idx on public.hso_issue_records(severity,verification_state);

create table if not exists public.hso_change_events (
  id uuid primary key default gen_random_uuid(),
  provider text not null check(provider in ('notion','github','internal')),
  delivery_id text not null,
  event_type text not null,
  external_subject text,
  title text not null,
  impact text not null default 'UNKNOWN',
  follow_up text not null default 'RECONCILE',
  related_work_item_id uuid references public.hso_work_items(id) on delete set null,
  related_milestone text,
  before_state jsonb not null default '{}'::jsonb,
  after_state jsonb not null default '{}'::jsonb,
  source_url text,
  event_at timestamptz not null default now(),
  unique(provider,delivery_id)
);
create index if not exists hso_change_events_time_idx on public.hso_change_events(event_at desc);

create table if not exists public.hso_completion_criteria (
  id uuid primary key default gen_random_uuid(),
  project_key text not null default 'hso',
  criterion_key text not null,
  title text not null,
  description text,
  required boolean not null default true,
  scope_weight numeric(12,2),
  state text not null default 'NOT_BUILT'
    check(state in ('NOT_BUILT','BUILDING','BUILT_UNVERIFIED','VERIFIED','ACCEPTED','BLOCKED')),
  source_key text references public.hso_sources(source_key),
  source_external_id text,
  evidence_record_id uuid references public.hso_evidence_records(id) on delete set null,
  acceptance_rule jsonb not null default '{}'::jsonb,
  last_evaluated_at timestamptz,
  unique(project_key,criterion_key),
  check(scope_weight is null or scope_weight>0)
);
create index if not exists hso_completion_criteria_state_idx on public.hso_completion_criteria(project_key,state,required);

create or replace view public.hso_verified_work_items_v with (security_invoker=true) as
select wi.*,
  exists(select 1 from public.hso_evidence_records ev
    where ev.source_key='notion-evidence-registry'
      and ev.related_work_item=wi.external_id
      and ev.evidence_state in ('PASS','VERIFIED','ACCEPTED')
      and ev.freshness='FRESH'
      and (ev.verified_at is not null or ev.evidence_type in ('Acceptance Test','Human Review','Release Verification'))
      and (wi.ci_commit_sha is null or ev.commit_sha=wi.ci_commit_sha)
      and (wi.head_commit_sha is null or ev.commit_sha=wi.head_commit_sha)
  ) as evidence_verified,
  (wi.execution_state in ('Verified','Accepted')
   and wi.gate_state='PASS'
   and wi.source_verified_at is not null
   and wi.source_verified_at>=now()-interval '7 days'
   and exists(select 1 from public.hso_evidence_records ev
      where ev.source_key='notion-evidence-registry'
        and ev.related_work_item=wi.external_id
        and ev.evidence_state in ('PASS','VERIFIED','ACCEPTED')
        and ev.freshness='FRESH'
        and (ev.verified_at is not null or ev.evidence_type in ('Acceptance Test','Human Review','Release Verification'))
        and (wi.ci_commit_sha is null or ev.commit_sha=wi.ci_commit_sha)
        and (wi.head_commit_sha is null or ev.commit_sha=wi.head_commit_sha)
   )) as verified_completion
from public.hso_work_items wi where wi.record_type='Work Item';

alter table public.hso_progress_snapshots enable row level security;
alter table public.hso_progress_snapshots force row level security;
alter table public.hso_decision_runs enable row level security;
alter table public.hso_decision_runs force row level security;
alter table public.hso_issue_records enable row level security;
alter table public.hso_issue_records force row level security;
alter table public.hso_change_events enable row level security;
alter table public.hso_change_events force row level security;
alter table public.hso_completion_criteria enable row level security;
alter table public.hso_completion_criteria force row level security;

revoke all on table public.hso_progress_snapshots,public.hso_decision_runs,public.hso_issue_records,public.hso_change_events,public.hso_completion_criteria from anon,authenticated;
grant select on table public.hso_progress_snapshots,public.hso_decision_runs,public.hso_issue_records,public.hso_change_events,public.hso_completion_criteria to authenticated;
grant all on table public.hso_progress_snapshots,public.hso_decision_runs,public.hso_issue_records,public.hso_change_events,public.hso_completion_criteria to service_role;

drop policy if exists hso_progress_snapshots_member_read on public.hso_progress_snapshots;
create policy hso_progress_snapshots_member_read on public.hso_progress_snapshots for select to authenticated
  using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
drop policy if exists hso_decision_runs_member_read on public.hso_decision_runs;
create policy hso_decision_runs_member_read on public.hso_decision_runs for select to authenticated
  using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
drop policy if exists hso_issue_records_member_read on public.hso_issue_records;
create policy hso_issue_records_member_read on public.hso_issue_records for select to authenticated
  using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
drop policy if exists hso_change_events_member_read on public.hso_change_events;
create policy hso_change_events_member_read on public.hso_change_events for select to authenticated
  using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));
drop policy if exists hso_completion_criteria_member_read on public.hso_completion_criteria;
create policy hso_completion_criteria_member_read on public.hso_completion_criteria for select to authenticated
  using(exists(select 1 from public.hso_members m where m.user_id=(select auth.uid()) and m.active=true));

alter table public.hso_prompt_artifacts
  add column if not exists prompt_payload jsonb not null default '{}'::jsonb,
  add column if not exists context_hash text,
  add column if not exists task_key text,
  add column if not exists created_from_decision_run uuid references public.hso_decision_runs(id) on delete set null;
