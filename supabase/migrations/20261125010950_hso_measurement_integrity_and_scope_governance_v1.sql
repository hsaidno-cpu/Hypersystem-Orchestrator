
alter table public.hso_source_snapshots
  add column if not exists is_complete boolean not null default false,
  add column if not exists pagination_complete boolean not null default false,
  add column if not exists pagination_pages integer not null default 0,
  add column if not exists page_count integer not null default 0,
  add column if not exists source_total_count integer,
  add column if not exists scope_hash text,
  add column if not exists completeness_state text not null default 'UNKNOWN';

alter table public.hso_sources
  add column if not exists last_complete_at timestamptz,
  add column if not exists last_record_count integer,
  add column if not exists last_scope_hash text;

alter table public.hso_work_items
  add column if not exists scope_inclusion_state text not null default 'PENDING',
  add column if not exists scope_decision_by text,
  add column if not exists scope_decision_at timestamptz,
  add column if not exists scope_decision_rationale text,
  add column if not exists scope_weight_approval text not null default 'PENDING',
  add column if not exists scope_weight_approved_by text,
  add column if not exists scope_weight_approved_at timestamptz;

alter table public.hso_progress_snapshots
  add column if not exists source_sync_run_id uuid references public.hso_sync_runs(id) on delete set null,
  add column if not exists scope_hash text,
  add column if not exists partial_weighted_progress_pct numeric,
  add column if not exists scope_decision_coverage_pct numeric,
  add column if not exists weight_approval_coverage_pct numeric,
  add column if not exists is_publishable boolean not null default false,
  add column if not exists measurement_reasons jsonb not null default '[]'::jsonb;

alter table public.hso_decision_runs
  add column if not exists source_sync_run_id uuid references public.hso_sync_runs(id) on delete set null,
  add column if not exists snapshot_coverage jsonb not null default '{}'::jsonb,
  add column if not exists decision_inputs_complete boolean not null default false;

do $$
begin
  if not exists (select 1 from pg_constraint where conname='hso_source_snapshots_completeness_state_check') then
    alter table public.hso_source_snapshots
      add constraint hso_source_snapshots_completeness_state_check
      check (completeness_state in ('UNKNOWN','COMPLETE','INCOMPLETE'));
  end if;
  if not exists (select 1 from pg_constraint where conname='hso_source_snapshots_pagination_pages_check') then
    alter table public.hso_source_snapshots
      add constraint hso_source_snapshots_pagination_pages_check check (pagination_pages >= 0 and page_count >= 0);
  end if;
  if not exists (select 1 from pg_constraint where conname='hso_work_items_scope_state_check') then
    alter table public.hso_work_items
      add constraint hso_work_items_scope_state_check
      check (scope_inclusion_state in ('PENDING','IN_SCOPE','OUT_OF_SCOPE'));
  end if;
  if not exists (select 1 from pg_constraint where conname='hso_work_items_weight_approval_check') then
    alter table public.hso_work_items
      add constraint hso_work_items_weight_approval_check
      check (scope_weight_approval in ('PENDING','APPROVED','REJECTED'));
  end if;
end $$;

create index if not exists hso_source_snapshots_run_source_idx
  on public.hso_source_snapshots(sync_run_id,source_key,observed_at desc);
create index if not exists hso_work_items_source_record_idx
  on public.hso_work_items(source_key,record_type);
create index if not exists hso_work_items_scope_state_idx
  on public.hso_work_items(scope_inclusion_state,scope_weight_approval);
create index if not exists hso_progress_snapshots_publishable_idx
  on public.hso_progress_snapshots(project_key,is_publishable,computed_at desc);

comment on column public.hso_source_snapshots.is_complete is
  'True only after every page/cursor for the source has been exhausted and verified.';
comment on column public.hso_source_snapshots.scope_hash is
  'SHA-256 fingerprint of the complete canonical source membership.';
comment on column public.hso_work_items.scope_inclusion_state is
  'Explicit owner decision for project denominator inclusion. PENDING suppresses project-wide progress.';
comment on column public.hso_work_items.scope_weight_approval is
  'Explicit approval state for numeric Scope Weight. Only APPROVED positive weights count toward publishable progress.';
comment on column public.hso_progress_snapshots.is_publishable is
  'True only when all mandatory source, scope, weight, evidence and completeness gates pass.';
