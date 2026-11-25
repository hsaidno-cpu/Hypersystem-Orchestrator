-- HSO Mission Control baseline-vs-actual milestone fields and execution relation.
alter table public.hso_work_items
  add column if not exists accountable_role text,
  add column if not exists expected_progress_pct numeric(5,2),
  add column if not exists baseline_start_date date;
alter table public.hso_executions add column if not exists related_work_item text;
alter table public.hso_progress_snapshots
  add column if not exists expected_progress_pct numeric(5,2),
  add column if not exists baseline_start_date date,
  add column if not exists target_date date;
