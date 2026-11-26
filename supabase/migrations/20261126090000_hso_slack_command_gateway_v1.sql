-- HSO Slack Command Gateway v1
-- Additive only. This migration does not enable execution or create credentials.
-- The Edge Function writes through service_role after verifying Slack's v0 signature
-- and the configured GOV-01 Slack user/team/channel allowlist.

create table if not exists public.hso_slack_commands (
  id uuid primary key default gen_random_uuid(),
  team_id text not null,
  channel_id text not null,
  actor_slack_user_id text not null,
  trigger_id text not null,
  command_name text not null check (
    command_name in ('instruction', 'priority', 'pause', 'stop', 'freeze', 'resume')
  ),
  arguments text not null default '',
  request_sha256 text not null check (request_sha256 ~ '^[0-9a-f]{64}$'),
  state text not null default 'pending_worker' check (
    state in (
      'pending_worker',
      'processing',
      'blocked_incomplete_persistence',
      'dispatched',
      'completed',
      'failed',
      'cancelled',
      'stale'
    )
  ),
  dispatch_enabled boolean not null default false,
  received_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  claimed_at timestamptz,
  finished_at timestamptz,
  result jsonb not null default '{}'::jsonb,
  unique (team_id, trigger_id)
);

create index if not exists hso_slack_commands_pending_idx
  on public.hso_slack_commands (received_at)
  where state = 'pending_worker';

create index if not exists hso_slack_commands_actor_idx
  on public.hso_slack_commands (actor_slack_user_id, received_at desc);

create table if not exists public.hso_command_outbox (
  id uuid primary key default gen_random_uuid(),
  command_id uuid not null references public.hso_slack_commands(id) on delete restrict,
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  state text not null default 'pending' check (
    state in ('pending', 'processing', 'delivered', 'failed', 'dead_letter')
  ),
  attempt_count integer not null default 0 check (attempt_count >= 0),
  next_attempt_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  last_error text,
  unique (command_id, event_type)
);

create index if not exists hso_command_outbox_pending_idx
  on public.hso_command_outbox (next_attempt_at, created_at)
  where state in ('pending', 'failed');

create table if not exists public.hso_slack_command_audit (
  id uuid primary key default gen_random_uuid(),
  command_id uuid references public.hso_slack_commands(id) on delete restrict,
  event_type text not null,
  actor_slack_user_id text not null,
  actor_role text not null,
  request_sha256 text check (request_sha256 is null or request_sha256 ~ '^[0-9a-f]{64}$'),
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists hso_slack_command_audit_command_idx
  on public.hso_slack_command_audit (command_id, created_at);

alter table public.hso_slack_commands enable row level security;
alter table public.hso_command_outbox enable row level security;
alter table public.hso_slack_command_audit enable row level security;

revoke all on table public.hso_slack_commands from public, anon, authenticated;
revoke all on table public.hso_command_outbox from public, anon, authenticated;
revoke all on table public.hso_slack_command_audit from public, anon, authenticated;

grant select, insert, update on table public.hso_slack_commands to service_role;
grant select, insert, update on table public.hso_command_outbox to service_role;
grant select, insert on table public.hso_slack_command_audit to service_role;

create or replace function public.hso_reject_slack_audit_mutation()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  raise exception 'hso_slack_command_audit is append-only';
end;
$$;

revoke all on function public.hso_reject_slack_audit_mutation() from public, anon, authenticated;
grant execute on function public.hso_reject_slack_audit_mutation() to service_role;

drop trigger if exists hso_slack_audit_no_update on public.hso_slack_command_audit;
create trigger hso_slack_audit_no_update
before update or delete on public.hso_slack_command_audit
for each row execute function public.hso_reject_slack_audit_mutation();

comment on table public.hso_slack_commands is
  'Signed GOV-01 Slack command intake. Queue state is not proof of execution.';
comment on table public.hso_command_outbox is
  'Durable outbox for future governed HSO workers; dispatch remains separately gated.';
comment on table public.hso_slack_command_audit is
  'Append-only record of Slack command ingress decisions; never stores Slack response_url or credentials.';
