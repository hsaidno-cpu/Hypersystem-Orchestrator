-- Disposable PostgreSQL smoke checks for PRE Kanban migrations.
-- The CI job bootstraps minimal Supabase roles/auth.uid() before applying migrations.
do $$
declare
  v_missing text;
  v_table text;
begin
  select string_agg(required.table_name, ', ' order by required.table_name)
  into v_missing
  from unnest(array[
    'kanban_workspaces',
    'kanban_workspace_members',
    'kanban_boards',
    'kanban_columns',
    'kanban_cards',
    'kanban_labels',
    'kanban_card_labels',
    'kanban_sync_runs',
    'kanban_sync_bindings',
    'kanban_sync_events',
    'kanban_audit_events',
    'kanban_sync_outbox'
  ]) as required(table_name)
  where to_regclass('public.' || required.table_name) is null;

  if v_missing is not null then
    raise exception 'missing Kanban tables: %', v_missing;
  end if;

  for v_table in
    select unnest(array[
      'kanban_workspaces',
      'kanban_workspace_members',
      'kanban_boards',
      'kanban_columns',
      'kanban_cards',
      'kanban_labels',
      'kanban_card_labels',
      'kanban_sync_runs',
      'kanban_sync_bindings',
      'kanban_sync_events',
      'kanban_audit_events',
      'kanban_sync_outbox'
    ])
  loop
    if not exists (
      select 1
      from pg_class c
      join pg_namespace n on n.oid = c.relnamespace
      where n.nspname = 'public'
        and c.relname = v_table
        and c.relrowsecurity
    ) then
      raise exception 'RLS is not enabled for public.%', v_table;
    end if;
  end loop;

  if has_table_privilege('authenticated','public.kanban_sync_runs','INSERT')
     or has_table_privilege('authenticated','public.kanban_sync_runs','UPDATE')
     or has_table_privilege('authenticated','public.kanban_sync_runs','DELETE') then
    raise exception 'authenticated role retains direct write privileges on kanban_sync_runs';
  end if;

  if has_table_privilege('authenticated','public.kanban_sync_bindings','INSERT')
     or has_table_privilege('authenticated','public.kanban_sync_bindings','UPDATE')
     or has_table_privilege('authenticated','public.kanban_sync_bindings','DELETE') then
    raise exception 'authenticated role retains direct write privileges on kanban_sync_bindings';
  end if;

  if has_table_privilege('authenticated','public.kanban_sync_events','INSERT')
     or has_table_privilege('authenticated','public.kanban_sync_events','UPDATE')
     or has_table_privilege('authenticated','public.kanban_sync_events','DELETE') then
    raise exception 'authenticated role retains direct write privileges on kanban_sync_events';
  end if;

  if has_table_privilege('authenticated','public.kanban_sync_outbox','UPDATE')
     or has_table_privilege('authenticated','public.kanban_sync_outbox','INSERT')
     or has_table_privilege('authenticated','public.kanban_sync_outbox','DELETE') then
    raise exception 'authenticated role retains direct write privileges on kanban_sync_outbox';
  end if;

  if has_table_privilege('authenticated','public.kanban_audit_events','UPDATE')
     or has_table_privilege('authenticated','public.kanban_audit_events','DELETE') then
    raise exception 'authenticated role can mutate append-only audit rows';
  end if;

  if to_regprocedure('public.kanban_claim_sync_run(uuid,text,uuid)') is null
     or to_regprocedure('public.kanban_apply_sync_item(uuid,uuid,jsonb)') is null
     or to_regprocedure('public.kanban_finalize_sync_run(uuid,uuid,integer,integer,jsonb)') is null
     or to_regprocedure('public.kanban_create_sync_preview(uuid,uuid,text,text,text,jsonb)') is null
     or to_regprocedure('public.kanban_record_sync_readback(uuid,integer,integer)') is null
     or to_regprocedure('public.kanban_ack_sync_outbox(uuid,integer,text,text,text)') is null
     or to_regprocedure('public.kanban_mark_sync_outbox_conflict(uuid,text)') is null
     or to_regprocedure('public.kanban_create_card(uuid,uuid,uuid,text,text,text,text,date,jsonb)') is null
     or to_regprocedure('public.kanban_move_card(uuid,uuid,integer)') is null then
    raise exception 'one or more required Kanban RPC signatures are missing';
  end if;

  if not has_function_privilege('authenticated','public.kanban_create_sync_preview(uuid,uuid,text,text,text,jsonb)','EXECUTE')
     or not has_function_privilege('authenticated','public.kanban_claim_sync_run(uuid,text,uuid)','EXECUTE')
     or not has_function_privilege('authenticated','public.kanban_apply_sync_item(uuid,uuid,jsonb)','EXECUTE')
     or has_function_privilege('anon','public.kanban_apply_sync_item(uuid,uuid,jsonb)','EXECUTE') then
    raise exception 'Kanban RPC execution grants do not match the intended authenticated/anon boundary';
  end if;
end;
$$;

select 'PRE Kanban PostgreSQL migration smoke checks passed' as result;
