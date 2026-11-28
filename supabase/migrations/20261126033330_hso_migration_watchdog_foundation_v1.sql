-- HSO Migration Watchdog v1: isolated evidence ledger, RLS, Vault-backed auth and cron.
-- Source scanning is read-only. The worker cannot publish, modify plugins or mark capabilities VERIFIED.

create extension if not exists pg_cron with schema pg_catalog;
create extension if not exists pg_net with schema extensions;

create table if not exists public.hso_migration_runs (
  id uuid primary key default gen_random_uuid(),
  run_key uuid not null unique,
  trigger_kind text not null check (trigger_kind in ('scheduled','manual')),
  status text not null default 'running' check (status in ('running','partial','succeeded','failed')),
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  source_boundary_count integer not null default 0 check (source_boundary_count >= 0),
  path_count integer not null default 0 check (path_count >= 0),
  unique_blob_count integer not null default 0 check (unique_blob_count >= 0),
  duplicate_path_rows integer not null default 0 check (duplicate_path_rows >= 0),
  content_verified_count integer not null default 0 check (content_verified_count >= 0),
  content_pending_count integer not null default 0 check (content_pending_count >= 0),
  content_failed_count integer not null default 0 check (content_failed_count >= 0),
  capability_count integer not null default 0 check (capability_count >= 0),
  accepted_capability_count integer not null default 0 check (accepted_capability_count >= 0),
  summary jsonb not null default '{}'::jsonb,
  error_summary text
);

create table if not exists public.hso_migration_sources (
  boundary_key text primary key,
  repository_full_name text not null,
  commit_sha text not null,
  visibility text not null check (visibility in ('public','private')),
  expected_blob_paths integer not null check (expected_blob_paths >= 0),
  observed_blob_paths integer check (observed_blob_paths >= 0),
  tree_sha text,
  tree_truncated boolean not null default false,
  status text not null default 'NOT_SCANNED',
  last_scanned_at timestamptz,
  last_error text,
  latest_run_id uuid references public.hso_migration_runs(id) on delete set null
);

create table if not exists public.hso_migration_paths (
  boundary_key text not null references public.hso_migration_sources(boundary_key) on delete cascade,
  repository_full_name text not null,
  source_commit text not null,
  path text not null,
  blob_sha text not null,
  size_bytes bigint not null default 0 check (size_bytes >= 0),
  file_mode text not null default '100644',
  observed_at timestamptz not null default now(),
  primary key (boundary_key, path)
);

create index if not exists hso_migration_paths_blob_sha_idx
  on public.hso_migration_paths(blob_sha);
create index if not exists hso_migration_paths_commit_idx
  on public.hso_migration_paths(repository_full_name, source_commit);

create table if not exists public.hso_migration_blobs (
  blob_sha text primary key,
  size_bytes bigint not null default 0 check (size_bytes >= 0),
  content_status text not null default 'pending'
    check (content_status in ('pending','private_access_pending','verified','mismatch','failed','too_large_or_unsupported')),
  source_repository_full_name text not null,
  source_boundary_key text not null,
  source_path text not null,
  source_visibility text not null check (source_visibility in ('public','private')),
  content_sha256 text,
  actual_git_blob_sha text,
  byte_length bigint,
  sha_verified boolean not null default false,
  semantic_review_state text not null default 'NOT_REVIEWED',
  attempt_count integer not null default 0 check (attempt_count >= 0),
  first_read_at timestamptz,
  last_read_at timestamptz,
  last_error text,
  updated_at timestamptz not null default now()
);

create index if not exists hso_migration_blobs_pending_idx
  on public.hso_migration_blobs(content_status, size_bytes);
create index if not exists hso_migration_blobs_verified_idx
  on public.hso_migration_blobs(sha_verified);

create table if not exists public.hso_migration_capabilities (
  plugin_key text not null,
  skill_name text not null,
  source_uri text,
  description text,
  instruction_bundle_path text,
  snapshot_origin text,
  package_version text,
  git_source_version text,
  catalog_source_state text not null default 'UNSET',
  catalog_parity_state text not null default 'NOT_ASSESSED',
  snapshot_commit text not null,
  snapshot_blob_sha text not null,
  observed_at timestamptz not null default now(),
  primary key (plugin_key, skill_name)
);

create table if not exists public.hso_migration_capability_assessments (
  plugin_key text not null,
  skill_name text not null,
  source_parity_state text not null default 'NOT_ASSESSED',
  contract_test_state text not null default 'NOT_RUN',
  route_test_state text not null default 'NOT_RUN',
  runtime_state text not null default 'NOT_RUN',
  acceptance_state text not null default 'OPEN',
  evidence jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (plugin_key, skill_name),
  foreign key (plugin_key, skill_name)
    references public.hso_migration_capabilities(plugin_key, skill_name)
    on delete cascade
);

create table if not exists public.hso_migration_runtime_receipts (
  invocation_id uuid primary key,
  plugin_key text not null,
  skill_name text not null,
  source_commit text not null,
  package_version text not null,
  runtime_id text not null,
  status text not null,
  input_digest text,
  output_digest text,
  receipt jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.hso_migration_control (
  id smallint primary key check (id = 1),
  lease_token uuid,
  lease_expires_at timestamptz,
  updated_at timestamptz not null default now()
);
insert into public.hso_migration_control(id) values (1)
on conflict (id) do nothing;

alter table public.hso_migration_runs enable row level security;
alter table public.hso_migration_sources enable row level security;
alter table public.hso_migration_paths enable row level security;
alter table public.hso_migration_blobs enable row level security;
alter table public.hso_migration_capabilities enable row level security;
alter table public.hso_migration_capability_assessments enable row level security;
alter table public.hso_migration_runtime_receipts enable row level security;
alter table public.hso_migration_control enable row level security;

revoke all on public.hso_migration_runs from public, anon, authenticated;
revoke all on public.hso_migration_sources from public, anon, authenticated;
revoke all on public.hso_migration_paths from public, anon, authenticated;
revoke all on public.hso_migration_blobs from public, anon, authenticated;
revoke all on public.hso_migration_capabilities from public, anon, authenticated;
revoke all on public.hso_migration_capability_assessments from public, anon, authenticated;
revoke all on public.hso_migration_runtime_receipts from public, anon, authenticated;
revoke all on public.hso_migration_control from public, anon, authenticated;

grant select, insert, update, delete on public.hso_migration_runs to service_role;
grant select, insert, update, delete on public.hso_migration_sources to service_role;
grant select, insert, update, delete on public.hso_migration_paths to service_role;
grant select, insert, update, delete on public.hso_migration_blobs to service_role;
grant select, insert, update, delete on public.hso_migration_capabilities to service_role;
grant select, insert, update, delete on public.hso_migration_capability_assessments to service_role;
grant select, insert, update, delete on public.hso_migration_runtime_receipts to service_role;
grant select, insert, update, delete on public.hso_migration_control to service_role;

create or replace function public.hso_try_claim_migration_watchdog(p_lease_token uuid)
returns boolean
language plpgsql
security invoker
set search_path = pg_catalog, public
as $$
begin
  update public.hso_migration_control
     set lease_token = p_lease_token,
         lease_expires_at = now() + interval '15 minutes',
         updated_at = now()
   where id = 1
     and (lease_expires_at is null or lease_expires_at < now());
  return found;
end;
$$;

create or replace function public.hso_release_migration_watchdog(p_lease_token uuid)
returns boolean
language plpgsql
security invoker
set search_path = pg_catalog, public
as $$
begin
  update public.hso_migration_control
     set lease_token = null,
         lease_expires_at = null,
         updated_at = now()
   where id = 1
     and lease_token = p_lease_token;
  return found;
end;
$$;

create or replace function public.hso_verify_migration_token(p_token text)
returns boolean
language sql
stable
security invoker
set search_path = pg_catalog, vault, extensions
as $$
  select coalesce(
    p_token is not null
    and length(p_token) >= 32
    and exists (
      select 1
        from vault.decrypted_secrets s
       where s.name = 'hso_migration_watchdog_token'
         and extensions.digest(s.decrypted_secret, 'sha256') =
             extensions.digest(p_token, 'sha256')
    ),
    false
  );
$$;

create or replace function public.hso_get_migration_github_read_token()
returns text
language sql
stable
security invoker
set search_path = pg_catalog, vault
as $$
  select s.decrypted_secret
    from vault.decrypted_secrets s
   where s.name = 'hso_github_read_token'
   limit 1;
$$;

revoke all on function public.hso_try_claim_migration_watchdog(uuid) from public, anon, authenticated;
revoke all on function public.hso_release_migration_watchdog(uuid) from public, anon, authenticated;
revoke all on function public.hso_verify_migration_token(text) from public, anon, authenticated;
revoke all on function public.hso_get_migration_github_read_token() from public, anon, authenticated;

grant execute on function public.hso_try_claim_migration_watchdog(uuid) to service_role;
grant execute on function public.hso_release_migration_watchdog(uuid) to service_role;
grant execute on function public.hso_verify_migration_token(text) to service_role;
grant execute on function public.hso_get_migration_github_read_token() to service_role;

do $$
begin
  if not exists (select 1 from vault.secrets where name = 'hso_migration_watchdog_token') then
    perform vault.create_secret(
      encode(extensions.gen_random_bytes(32), 'hex'),
      'hso_migration_watchdog_token',
      'Private bearer token for HSO Migration Watchdog Edge Function',
      null
    );
  end if;

  if not exists (select 1 from vault.secrets where name = 'hso_migration_watchdog_apikey') then
    perform vault.create_secret(
      'sb_publishable_WEGw3SplkYTFbMCvCuPW1A_gkDpUARk',
      'hso_migration_watchdog_apikey',
      'Supabase publishable project key used by pg_net to call the HSO Migration Watchdog Edge Function',
      null
    );
  end if;
end;
$$;

revoke all on schema net from public, anon, authenticated;
grant usage on schema net to postgres;
revoke all on schema cron from public, anon, authenticated;
grant usage on schema cron to postgres;

do $$
declare
  job_row record;
begin
  for job_row in select jobid from cron.job where jobname = 'hso-migration-watchdog'
  loop
    perform cron.unschedule(job_row.jobid);
  end loop;

  perform cron.schedule(
    'hso-migration-watchdog',
    '17 */2 * * *',
    $job$
      select net.http_post(
        url := 'https://ehgmtkkppmceaffhwcpc.supabase.co/functions/v1/hso-migration-watchdog',
        headers := jsonb_build_object(
          'Content-Type', 'application/json',
          'apikey', (select decrypted_secret from vault.decrypted_secrets where name = 'hso_migration_watchdog_apikey'),
          'x-hso-migration-token', (select decrypted_secret from vault.decrypted_secrets where name = 'hso_migration_watchdog_token')
        ),
        body := '{"trigger_kind":"scheduled","max_blob_reads":16}'::jsonb,
        timeout_milliseconds := 10000
      ) as request_id;
    $job$
  );
end;
$$;

comment on table public.hso_migration_runs is 'Immutable execution receipts for the HSO source/capability migration watchdog.';
comment on table public.hso_migration_paths is 'Every source path retained with its repository, immutable commit and Git blob SHA.';
comment on table public.hso_migration_blobs is 'Deduplicated Git blob payload verification state; content bytes are never persisted.';
comment on table public.hso_migration_capabilities is 'Snapshot inventory of 289 HSO skill metadata records; not parity/runtime acceptance.';
comment on table public.hso_migration_runtime_receipts is 'Future host invocation receipts; no runtime is auto-enabled by the watchdog.';
