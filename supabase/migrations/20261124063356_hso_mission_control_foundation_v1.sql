-- HSO Mission Control foundation v1; isolated to hso_* tables.
create table if not exists public.hso_sources (
 source_key text primary key, provider text not null check(provider in ('notion','github','internal')),
 display_name text not null, authority_role text not null, source_uri text, enabled boolean not null default true,
 status text not null default 'not_configured' check(status in ('not_configured','connected','degraded','disabled')),
 last_event_at timestamptz, last_sync_at timestamptz, last_success_at timestamptz,
 freshness_seconds integer not null default 1800 check(freshness_seconds>0), last_error text,
 metadata jsonb not null default '{}'::jsonb, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.hso_sync_runs (
 id uuid primary key default gen_random_uuid(), trigger_kind text not null check(trigger_kind in ('manual','webhook','scheduled','initial','recovery')),
 status text not null default 'running' check(status in ('running','succeeded','partial','failed')),
 started_at timestamptz not null default now(), finished_at timestamptz, source_results jsonb not null default '{}'::jsonb,
 records_seen integer not null default 0, records_upserted integer not null default 0, error_summary text,
 correlation_id text, created_at timestamptz not null default now()
);
create table if not exists public.hso_integration_events (
 id uuid primary key default gen_random_uuid(), provider text not null check(provider in ('notion','github','internal')),
 delivery_id text not null, event_type text not null, external_subject text, payload_hash text not null,
 payload jsonb not null default '{}'::jsonb,
 processing_state text not null default 'received' check(processing_state in ('received','processing','processed','ignored','failed')),
 received_at timestamptz not null default now(), processed_at timestamptz, last_error text,
 unique(provider,delivery_id)
);
create table if not exists public.hso_source_snapshots (
 id uuid primary key default gen_random_uuid(), source_key text not null references public.hso_sources(source_key),
 sync_run_id uuid references public.hso_sync_runs(id) on delete set null, observed_at timestamptz not null default now(),
 content_hash text not null, freshness text not null default 'FRESH' check(freshness in ('FRESH','STALE','UNKNOWN','NOT_APPLICABLE')),
 record_count integer not null default 0, snapshot jsonb not null default '{}'::jsonb
);
create index if not exists hso_source_snapshots_source_observed_idx on public.hso_source_snapshots(source_key,observed_at desc);
create table if not exists public.hso_work_items (
 id uuid primary key default gen_random_uuid(), source_key text not null references public.hso_sources(source_key),
 external_id text not null, item_key text, title text not null, execution_state text not null default 'UNKNOWN',
 verification_state text not null default 'UNKNOWN', gate_state text not null default 'NOT_ASSESSED',
 priority text, pre_stage text, ecosystem_stage text, dependencies jsonb not null default '[]'::jsonb,
 next_action text, blocker text, source_url text, source_updated_at timestamptz,
 observed_at timestamptz not null default now(), raw_properties jsonb not null default '{}'::jsonb,
 unique(source_key,external_id)
);
create index if not exists hso_work_items_state_idx on public.hso_work_items(execution_state,gate_state);
create index if not exists hso_work_items_priority_idx on public.hso_work_items(priority,observed_at desc);
create table if not exists public.hso_executions (
 id uuid primary key default gen_random_uuid(), source_key text not null references public.hso_sources(source_key),
 external_id text not null, run_name text not null, correlation_id text, owner_role text, pre_stage text,
 status text not null default 'UNKNOWN', github_run_id text, github_workflow_url text, execution_receipt_url text,
 audit_url text, failure_recovery_summary text, retry_count integer not null default 0, completed_at timestamptz,
 source_url text, observed_at timestamptz not null default now(), raw_properties jsonb not null default '{}'::jsonb,
 unique(source_key,external_id)
);
create table if not exists public.hso_evidence_records (
 id uuid primary key default gen_random_uuid(), source_key text not null references public.hso_sources(source_key),
 external_id text not null, title text not null, evidence_type text not null default 'External Source',
 evidence_state text not null default 'UNKNOWN', freshness text not null default 'UNKNOWN', repository_url text,
 branch_ref text, commit_sha text, pr_url text, ci_run_url text, artifact_url text, claim_supported text,
 known_limitation text, observed_at timestamptz not null default now(), source_url text, payload jsonb not null default '{}'::jsonb,
 unique(source_key,external_id)
);
create index if not exists hso_evidence_records_commit_idx on public.hso_evidence_records(commit_sha);
create index if not exists hso_evidence_records_state_idx on public.hso_evidence_records(evidence_state,freshness);
create table if not exists public.hso_decisions (
 id uuid primary key default gen_random_uuid(), work_item_id uuid references public.hso_work_items(id) on delete set null,
 decision_type text not null, eligibility_state text not null, priority_score numeric(6,2),
 policy_version text not null, rationale jsonb not null default '{}'::jsonb,
 evidence_snapshot_id uuid references public.hso_source_snapshots(id) on delete set null, computed_at timestamptz not null default now()
);
create index if not exists hso_decisions_latest_idx on public.hso_decisions(computed_at desc);
create table if not exists public.hso_prompt_artifacts (
 id uuid primary key default gen_random_uuid(), work_item_id uuid references public.hso_work_items(id) on delete set null,
 snapshot_id uuid references public.hso_source_snapshots(id) on delete set null, prompt_version text not null,
 prompt_text text not null, prompt_state text not null default 'generated' check(prompt_state in ('generated','stale','approved','consumed','revoked')),
 created_at timestamptz not null default now()
);
create table if not exists public.hso_notifications (
 id uuid primary key default gen_random_uuid(), dedupe_key text not null unique,
 severity text not null check(severity in ('info','warning','error','critical')), category text not null,
 message text not null, source_key text references public.hso_sources(source_key), external_id text,
 state text not null default 'open' check(state in ('open','acknowledged','resolved')),
 created_at timestamptz not null default now(), resolved_at timestamptz, metadata jsonb not null default '{}'::jsonb
);
insert into public.hso_sources(source_key,provider,display_name,authority_role,source_uri,status,freshness_seconds) values
('notion-control-center','notion','HSO Master Control Center','governance_and_authority','https://app.notion.com/p/42299868397f81b3b8a2d4f936f355cb','not_configured',1800),
('notion-roadmap','notion','HSO Master Roadmap & Milestones','roadmap_and_milestones','https://app.notion.com/p/42299868397f81d09bc2ff5885fd6471','not_configured',1800),
('notion-execution-ledger','notion','HSO Workflow Execution Ledger','execution_records','https://app.notion.com/p/42299868397f81c89570eeafc780bf91','not_configured',1800),
('notion-evidence-registry','notion','HSO Evidence Registry','evidence_index','https://app.notion.com/p/42299868397f816ab7efd69ae66e3a77','not_configured',1800),
('github-hso-parent','github','Hypersystem-Orchestrator repository','engineering_source_of_truth','https://github.com/hsaidno-cpu/Hypersystem-Orchestrator','not_configured',900)
on conflict(source_key) do update set display_name=excluded.display_name,authority_role=excluded.authority_role,source_uri=excluded.source_uri,freshness_seconds=excluded.freshness_seconds,updated_at=now();
alter table public.hso_sources enable row level security; alter table public.hso_sources force row level security;
alter table public.hso_sync_runs enable row level security; alter table public.hso_sync_runs force row level security;
alter table public.hso_integration_events enable row level security; alter table public.hso_integration_events force row level security;
alter table public.hso_source_snapshots enable row level security; alter table public.hso_source_snapshots force row level security;
alter table public.hso_work_items enable row level security; alter table public.hso_work_items force row level security;
alter table public.hso_executions enable row level security; alter table public.hso_executions force row level security;
alter table public.hso_evidence_records enable row level security; alter table public.hso_evidence_records force row level security;
alter table public.hso_decisions enable row level security; alter table public.hso_decisions force row level security;
alter table public.hso_prompt_artifacts enable row level security; alter table public.hso_prompt_artifacts force row level security;
alter table public.hso_notifications enable row level security; alter table public.hso_notifications force row level security;
revoke all on table public.hso_sources,public.hso_sync_runs,public.hso_integration_events,public.hso_source_snapshots,public.hso_work_items,public.hso_executions,public.hso_evidence_records,public.hso_decisions,public.hso_prompt_artifacts,public.hso_notifications from anon,authenticated;
grant all on table public.hso_sources,public.hso_sync_runs,public.hso_integration_events,public.hso_source_snapshots,public.hso_work_items,public.hso_executions,public.hso_evidence_records,public.hso_decisions,public.hso_prompt_artifacts,public.hso_notifications to service_role;
comment on table public.hso_integration_events is 'Webhook/event inbox with provider delivery deduplication. Payloads must be sanitized and never include secrets.';
comment on table public.hso_source_snapshots is 'Immutable source snapshots used for evidence-based reconciliation and decision reproducibility.';
comment on table public.hso_decisions is 'Derived recommendations only; cannot mutate source authority or create approvals.';
