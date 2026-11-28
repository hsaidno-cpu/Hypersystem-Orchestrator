-- PRE Kanban persistent backend foundation v1.
-- Source-only until reviewed, applied to a development database, and accepted.
create schema if not exists kanban_private;
revoke all on schema kanban_private from public, anon;
grant usage on schema kanban_private to authenticated;

create table if not exists public.kanban_workspaces (
  id uuid primary key default gen_random_uuid(),
  name text not null check (length(trim(name)) between 2 and 120),
  slug text not null unique check (slug ~ '^[a-z0-9][a-z0-9-]{1,62}$'),
  description text,
  created_by uuid not null references auth.users(id) on delete restrict,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.kanban_workspace_members (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.kanban_workspaces(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('owner','admin','editor','member','viewer')),
  status text not null default 'active' check (status in ('active','invited','disabled')),
  added_by uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now(),
  unique (workspace_id,user_id)
);

create table if not exists public.kanban_boards (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.kanban_workspaces(id) on delete cascade,
  name text not null check (length(trim(name)) between 2 and 160),
  slug text not null check (slug ~ '^[a-z0-9][a-z0-9-]{1,62}$'),
  description text,
  position integer not null default 1000,
  is_archived boolean not null default false,
  metadata jsonb not null default '{}'::jsonb,
  created_by uuid not null references auth.users(id),
  updated_by uuid not null references auth.users(id),
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (workspace_id,slug),
  unique (workspace_id,id)
);

create table if not exists public.kanban_columns (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  board_id uuid not null,
  name text not null check (length(trim(name)) between 1 and 80),
  semantic_key text not null check (semantic_key ~ '^[a-z][a-z0-9_-]{1,47}$'),
  position integer not null default 1000,
  color text not null default 'gray' check (color in ('gray','blue','green','yellow','orange','red','purple','pink')),
  wip_limit integer check (wip_limit is null or wip_limit > 0),
  is_archived boolean not null default false,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  foreign key (workspace_id,board_id) references public.kanban_boards(workspace_id,id) on delete cascade,
  unique (board_id,semantic_key),
  unique (board_id,id),
  unique (workspace_id,id)
);

create table if not exists public.kanban_cards (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  board_id uuid not null,
  column_id uuid not null,
  title text not null check (length(trim(title)) between 1 and 240),
  description text,
  priority text not null default 'medium' check (priority in ('critical','high','medium','low')),
  acceptance_criteria text,
  due_date date,
  position numeric(18,3) not null default 1000,
  is_archived boolean not null default false,
  archived_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_by uuid not null references auth.users(id),
  updated_by uuid not null references auth.users(id),
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  foreign key (workspace_id,board_id) references public.kanban_boards(workspace_id,id) on delete cascade,
  foreign key (board_id,column_id) references public.kanban_columns(board_id,id) on delete restrict,
  unique (board_id,id),
  unique (workspace_id,id)
);

create table if not exists public.kanban_labels (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  board_id uuid not null,
  name text not null check (length(trim(name)) between 1 and 48),
  color text not null default 'gray' check (color in ('gray','blue','green','yellow','orange','red','purple','pink')),
  created_by uuid not null references auth.users(id),
  created_at timestamptz not null default now(),
  foreign key (workspace_id,board_id) references public.kanban_boards(workspace_id,id) on delete cascade,
  unique (board_id,id)
);
create unique index if not exists kanban_labels_board_name_ci_idx
  on public.kanban_labels(board_id,lower(name));

create table if not exists public.kanban_card_labels (
  workspace_id uuid not null,
  board_id uuid not null,
  card_id uuid not null,
  label_id uuid not null,
  assigned_by uuid not null references auth.users(id),
  assigned_at timestamptz not null default now(),
  primary key (card_id,label_id),
  foreign key (workspace_id,board_id) references public.kanban_boards(workspace_id,id) on delete cascade,
  foreign key (board_id,card_id) references public.kanban_cards(board_id,id) on delete cascade,
  foreign key (board_id,label_id) references public.kanban_labels(board_id,id) on delete cascade
);

create table if not exists public.kanban_sync_runs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  board_id uuid not null,
  source_system text not null check (source_system in ('pre','hso','notion','github')),
  direction text not null check (direction in ('source_to_board','board_to_source','bidirectional')),
  status text not null default 'PREVIEWED' check (status in ('PREVIEWED','APPLYING','APPLIED','PARTIAL','FAILED','EXPIRED')),
  payload_digest text not null check (payload_digest ~ '^[a-f0-9]{64}$'),
  preview_plan jsonb not null default '{}'::jsonb,
  result_summary jsonb not null default '{}'::jsonb,
  source_count integer not null default 0 check (source_count >= 0),
  applied_count integer not null default 0 check (applied_count >= 0),
  conflict_count integer not null default 0 check (conflict_count >= 0),
  expires_at timestamptz not null default (now() + interval '15 minutes'),
  initiated_by uuid not null references auth.users(id),
  created_at timestamptz not null default now(),
  applied_at timestamptz,
  foreign key (workspace_id,board_id) references public.kanban_boards(workspace_id,id) on delete cascade
);

create table if not exists public.kanban_sync_bindings (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  board_id uuid not null,
  card_id uuid not null,
  source_system text not null check (source_system in ('pre','hso','notion','github')),
  source_work_item_id text not null check (length(source_work_item_id) between 1 and 240),
  source_revision text,
  last_source_digest text not null check (last_source_digest ~ '^[a-f0-9]{64}$'),
  last_board_revision integer not null check (last_board_revision > 0),
  last_synced_at timestamptz not null default now(),
  sync_direction text not null default 'source_to_board' check (sync_direction in ('source_to_board','board_to_source','bidirectional')),
  foreign key (workspace_id,board_id) references public.kanban_boards(workspace_id,id) on delete cascade,
  foreign key (board_id,card_id) references public.kanban_cards(board_id,id) on delete cascade,
  unique (workspace_id,source_system,source_work_item_id),
  unique (card_id)
);

create table if not exists public.kanban_sync_events (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.kanban_workspaces(id) on delete cascade,
  sync_run_id uuid references public.kanban_sync_runs(id) on delete set null,
  source_system text not null,
  source_work_item_id text,
  event_type text not null,
  disposition text not null check (disposition in ('CREATED','UPDATED','NOOP','CONFLICT','SKIPPED','FAILED','READ_BACK_PASS','READ_BACK_FAIL')),
  details jsonb not null default '{}'::jsonb,
  actor_user_id uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now()
);

create table if not exists public.kanban_audit_events (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.kanban_workspaces(id) on delete restrict,
  entity_type text not null,
  entity_id uuid not null,
  action text not null check (action in ('INSERT','UPDATE','DELETE')),
  actor_user_id uuid references auth.users(id) on delete set null,
  previous_revision integer,
  new_revision integer,
  request_id text,
  created_at timestamptz not null default now()
);

create index if not exists kanban_boards_workspace_position_idx on public.kanban_boards(workspace_id,is_archived,position);
create index if not exists kanban_columns_board_position_idx on public.kanban_columns(board_id,is_archived,position);
create index if not exists kanban_cards_board_column_position_idx on public.kanban_cards(board_id,column_id,is_archived,position);
create index if not exists kanban_sync_runs_workspace_created_idx on public.kanban_sync_runs(workspace_id,created_at desc);
create index if not exists kanban_sync_events_workspace_created_idx on public.kanban_sync_events(workspace_id,created_at desc);
create index if not exists kanban_audit_events_workspace_created_idx on public.kanban_audit_events(workspace_id,created_at desc);

create or replace function kanban_private.has_workspace_role(p_workspace_id uuid,p_roles text[] default array['owner','admin'])
returns boolean language sql stable security definer
set search_path = pg_catalog,public,auth
as $$
  select exists (
    select 1 from public.kanban_workspace_members m
    where m.workspace_id=p_workspace_id and m.user_id=auth.uid()
      and m.status='active' and m.role=any(p_roles)
  );
$$;
revoke all on function kanban_private.has_workspace_role(uuid,text[]) from public,anon;
grant execute on function kanban_private.has_workspace_role(uuid,text[]) to authenticated;

create or replace function kanban_private.add_workspace_owner()
returns trigger language plpgsql security definer
set search_path = pg_catalog,public,auth
as $$
begin
  insert into public.kanban_workspace_members(workspace_id,user_id,role,status,added_by)
  values(new.id,new.created_by,'owner','active',new.created_by)
  on conflict(workspace_id,user_id) do nothing;
  return new;
end;
$$;
revoke all on function kanban_private.add_workspace_owner() from public,anon,authenticated;
drop trigger if exists kanban_workspace_owner_after_insert on public.kanban_workspaces;
create trigger kanban_workspace_owner_after_insert after insert on public.kanban_workspaces
for each row execute function kanban_private.add_workspace_owner();

create or replace function kanban_private.touch_revision()
returns trigger language plpgsql set search_path = pg_catalog
as $$
begin
  new.updated_at=now();
  new.revision=old.revision+1;
  return new;
end;
$$;
revoke all on function kanban_private.touch_revision() from public,anon,authenticated;

do $$
declare t text;
begin
  foreach t in array array['kanban_workspaces','kanban_boards','kanban_columns','kanban_cards'] loop
    execute format('drop trigger if exists %I_touch_revision on public.%I',t,t);
    execute format('create trigger %I_touch_revision before update on public.%I for each row execute function kanban_private.touch_revision()',t,t);
  end loop;
end $$;

create or replace function kanban_private.audit_change()
returns trigger language plpgsql security definer
set search_path = pg_catalog,public,auth
as $$
declare
  v_row jsonb;
  v_workspace_id uuid;
  v_entity_id uuid;
  v_previous_revision integer;
  v_new_revision integer;
begin
  if tg_op='DELETE' then v_row=to_jsonb(old); else v_row=to_jsonb(new); end if;
  if tg_table_name='kanban_workspaces' then
    v_workspace_id=(v_row->>'id')::uuid;
  else
    v_workspace_id=(v_row->>'workspace_id')::uuid;
  end if;
  v_entity_id=(v_row->>'id')::uuid;
  if tg_op<>'INSERT' then v_previous_revision=nullif(to_jsonb(old)->>'revision','')::integer; end if;
  if tg_op<>'DELETE' then v_new_revision=nullif(to_jsonb(new)->>'revision','')::integer; end if;
  insert into public.kanban_audit_events(
    workspace_id,entity_type,entity_id,action,actor_user_id,previous_revision,new_revision,request_id
  ) values (
    v_workspace_id,tg_table_name,v_entity_id,tg_op,auth.uid(),v_previous_revision,v_new_revision,
    nullif((current_setting('request.headers',true)::jsonb)->>'x-request-id','')
  );
  if tg_op='DELETE' then return old; end if;
  return new;
end;
$$;
revoke all on function kanban_private.audit_change() from public,anon,authenticated;

create or replace function kanban_private.reject_audit_mutation()
returns trigger language plpgsql set search_path = pg_catalog
as $$ begin raise exception 'kanban_audit_events is append-only'; end; $$;
revoke all on function kanban_private.reject_audit_mutation() from public,anon,authenticated;
drop trigger if exists kanban_audit_events_no_mutation on public.kanban_audit_events;
create trigger kanban_audit_events_no_mutation before update or delete on public.kanban_audit_events
for each row execute function kanban_private.reject_audit_mutation();

do $$
declare t text;
begin
  foreach t in array array[
    'kanban_workspaces','kanban_workspace_members','kanban_boards','kanban_columns','kanban_cards',
    'kanban_labels','kanban_sync_runs','kanban_sync_bindings'
  ] loop
    execute format('drop trigger if exists %I_audit_change on public.%I',t,t);
    execute format('create trigger %I_audit_change after insert or update or delete on public.%I for each row execute function kanban_private.audit_change()',t,t);
  end loop;
end $$;

alter table public.kanban_workspaces enable row level security;
alter table public.kanban_workspace_members enable row level security;
alter table public.kanban_boards enable row level security;
alter table public.kanban_columns enable row level security;
alter table public.kanban_cards enable row level security;
alter table public.kanban_labels enable row level security;
alter table public.kanban_card_labels enable row level security;
alter table public.kanban_sync_runs enable row level security;
alter table public.kanban_sync_bindings enable row level security;
alter table public.kanban_sync_events enable row level security;
alter table public.kanban_audit_events enable row level security;

create policy kanban_workspaces_select on public.kanban_workspaces
for select to authenticated using (kanban_private.has_workspace_role(id,array['owner','admin','editor','member','viewer']));
create policy kanban_workspaces_insert on public.kanban_workspaces
for insert to authenticated with check (created_by=auth.uid());
create policy kanban_workspaces_update on public.kanban_workspaces
for update to authenticated using (kanban_private.has_workspace_role(id,array['owner','admin']))
with check (kanban_private.has_workspace_role(id,array['owner','admin']));

create policy kanban_members_select on public.kanban_workspace_members
for select to authenticated using (user_id=auth.uid() or kanban_private.has_workspace_role(workspace_id,array['owner','admin']));
create policy kanban_members_insert on public.kanban_workspace_members
for insert to authenticated with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin']));
create policy kanban_members_update on public.kanban_workspace_members
for update to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin']))
with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin']));

create policy kanban_boards_select on public.kanban_boards
for select to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor','member','viewer']));
create policy kanban_boards_insert on public.kanban_boards
for insert to authenticated with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));
create policy kanban_boards_update on public.kanban_boards
for update to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']))
with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));

create policy kanban_columns_select on public.kanban_columns
for select to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor','member','viewer']));
create policy kanban_columns_insert on public.kanban_columns
for insert to authenticated with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));
create policy kanban_columns_update on public.kanban_columns
for update to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']))
with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));

create policy kanban_cards_select on public.kanban_cards
for select to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor','member','viewer']));
create policy kanban_cards_insert on public.kanban_cards
for insert to authenticated with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor','member']));
create policy kanban_cards_update on public.kanban_cards
for update to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor','member']))
with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor','member']));

create policy kanban_labels_select on public.kanban_labels
for select to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor','member','viewer']));
create policy kanban_labels_insert on public.kanban_labels
for insert to authenticated with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));
create policy kanban_labels_update on public.kanban_labels
for update to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']))
with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));

create policy kanban_card_labels_select on public.kanban_card_labels
for select to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor','member','viewer']));
create policy kanban_card_labels_insert on public.kanban_card_labels
for insert to authenticated with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor','member']));
create policy kanban_card_labels_delete on public.kanban_card_labels
for delete to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor','member']));

create policy kanban_sync_runs_select on public.kanban_sync_runs
for select to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));
create policy kanban_sync_runs_insert on public.kanban_sync_runs
for insert to authenticated with check (initiated_by=auth.uid() and kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));
create policy kanban_sync_runs_update on public.kanban_sync_runs
for update to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']))
with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));

create policy kanban_sync_bindings_select on public.kanban_sync_bindings
for select to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));
create policy kanban_sync_bindings_insert on public.kanban_sync_bindings
for insert to authenticated with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));
create policy kanban_sync_bindings_update on public.kanban_sync_bindings
for update to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']))
with check (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));

create policy kanban_sync_events_select on public.kanban_sync_events
for select to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));
create policy kanban_sync_events_insert on public.kanban_sync_events
for insert to authenticated with check (actor_user_id=auth.uid() and kanban_private.has_workspace_role(workspace_id,array['owner','admin','editor']));

create policy kanban_audit_events_select on public.kanban_audit_events
for select to authenticated using (kanban_private.has_workspace_role(workspace_id,array['owner','admin']));

grant usage on schema public to authenticated;
grant select,insert,update on public.kanban_workspaces to authenticated;
grant select,insert,update on public.kanban_workspace_members to authenticated;
grant select,insert,update on public.kanban_boards to authenticated;
grant select,insert,update on public.kanban_columns to authenticated;
grant select,insert,update on public.kanban_cards to authenticated;
grant select,insert,update on public.kanban_labels to authenticated;
grant select,insert,delete on public.kanban_card_labels to authenticated;
grant select,insert,update on public.kanban_sync_runs to authenticated;
grant select,insert,update on public.kanban_sync_bindings to authenticated;
grant select,insert on public.kanban_sync_events to authenticated;
grant select on public.kanban_audit_events to authenticated;
revoke all on public.kanban_audit_events from anon;
revoke update,delete on public.kanban_audit_events from authenticated;

create or replace function public.kanban_create_board(
  p_workspace_id uuid,p_name text,p_slug text,p_description text default null,
  p_columns jsonb default '[
    {"name":"Backlog","semantic_key":"backlog","color":"gray"},
    {"name":"Ready","semantic_key":"ready","color":"blue"},
    {"name":"In Progress","semantic_key":"in_progress","color":"yellow"},
    {"name":"Blocked","semantic_key":"blocked","color":"red"},
    {"name":"Review & Verification","semantic_key":"review","color":"purple"},
    {"name":"Done","semantic_key":"done","color":"green"}
  ]'::jsonb
)
returns jsonb language plpgsql security invoker
set search_path = pg_catalog,public,kanban_private,auth
as $$
declare
  v_board public.kanban_boards;
  v_column jsonb;
  v_position integer=1000;
  v_columns jsonb='[]'::jsonb;
  v_name text;
  v_key text;
  v_color text;
begin
  if not kanban_private.has_workspace_role(p_workspace_id,array['owner','admin','editor']) then
    raise exception 'workspace_write_forbidden' using errcode='42501';
  end if;
  if jsonb_typeof(p_columns)<>'array' or jsonb_array_length(p_columns)<1 or jsonb_array_length(p_columns)>20 then
    raise exception 'columns_must_be_array_with_1_to_20_entries' using errcode='22023';
  end if;
  insert into public.kanban_boards(workspace_id,name,slug,description,created_by,updated_by)
  values(p_workspace_id,trim(p_name),lower(trim(p_slug)),p_description,auth.uid(),auth.uid())
  returning * into v_board;
  for v_column in select value from jsonb_array_elements(p_columns) loop
    v_name=trim(v_column->>'name');
    v_key=lower(trim(v_column->>'semantic_key'));
    v_color=coalesce(v_column->>'color','gray');
    if v_name is null or v_name='' or v_key !~ '^[a-z][a-z0-9_-]{1,47}$' then
      raise exception 'invalid_column_definition' using errcode='22023';
    end if;
    insert into public.kanban_columns(workspace_id,board_id,name,semantic_key,position,color)
    values(p_workspace_id,v_board.id,v_name,v_key,v_position,v_color);
    v_position=v_position+1000;
  end loop;
  select coalesce(jsonb_agg(to_jsonb(c) order by c.position),'[]'::jsonb)
  into v_columns from public.kanban_columns c where c.board_id=v_board.id;
  return jsonb_build_object('board',to_jsonb(v_board),'columns',v_columns);
end;
$$;
revoke all on function public.kanban_create_board(uuid,text,text,text,jsonb) from public,anon;
grant execute on function public.kanban_create_board(uuid,text,text,text,jsonb) to authenticated;

create or replace function public.kanban_reorder_columns(p_board_id uuid,p_column_ids uuid[])
returns jsonb language plpgsql security invoker
set search_path = pg_catalog,public,kanban_private
as $$
declare
  v_workspace_id uuid;
  v_count integer;
  v_updated integer;
begin
  select workspace_id into v_workspace_id from public.kanban_boards where id=p_board_id;
  if v_workspace_id is null or not kanban_private.has_workspace_role(v_workspace_id,array['owner','admin','editor']) then
    raise exception 'board_write_forbidden' using errcode='42501';
  end if;
  select count(*) into v_count from public.kanban_columns where board_id=p_board_id and not is_archived;
  if cardinality(p_column_ids)<>v_count
     or (select count(distinct ids.id) from unnest(p_column_ids) as ids(id))<>v_count
     or exists(
       select 1 from unnest(p_column_ids) as ids(id)
       left join public.kanban_columns c on c.id=ids.id and c.board_id=p_board_id
       where c.id is null
     ) then
    raise exception 'column_order_must_contain_every_active_column_once' using errcode='22023';
  end if;
  update public.kanban_columns c set position=ordered.ordinality*1000
  from unnest(p_column_ids) with ordinality as ordered(id,ordinality)
  where c.id=ordered.id and c.board_id=p_board_id;
  get diagnostics v_updated=row_count;
  return jsonb_build_object('board_id',p_board_id,'reordered',v_updated);
end;
$$;
revoke all on function public.kanban_reorder_columns(uuid,uuid[]) from public,anon;
grant execute on function public.kanban_reorder_columns(uuid,uuid[]) to authenticated;

comment on table public.kanban_workspaces is 'Tenant boundary for PRE Kanban; RLS access is controlled by active workspace membership.';
comment on table public.kanban_cards is 'Persistent Kanban cards. Revisions increment server-side for optimistic concurrency.';
comment on table public.kanban_sync_bindings is 'Stable mapping between PRE/HSO source work items and Kanban cards.';
comment on table public.kanban_audit_events is 'Append-only operational audit metadata. Not equivalent to external WORM anchoring.';
