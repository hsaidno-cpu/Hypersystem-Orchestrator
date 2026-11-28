-- Atomic card creation and movement with board-level ordering and WIP checks.
create or replace function public.kanban_create_card(
  p_workspace_id uuid,
  p_board_id uuid,
  p_column_id uuid,
  p_title text,
  p_description text default null,
  p_priority text default 'medium',
  p_acceptance_criteria text default null,
  p_due_date date default null,
  p_metadata jsonb default '{}'::jsonb
)
returns jsonb
language plpgsql
security invoker
set search_path = pg_catalog,public,kanban_private,auth
as $$
declare
  v_workspace_id uuid;
  v_column public.kanban_columns;
  v_position numeric;
  v_count integer;
  v_card public.kanban_cards;
begin
  if nullif(btrim(p_acceptance_criteria), '') is null
     or length(p_acceptance_criteria) > 8000 then
    raise exception 'card_acceptance_criteria_required' using errcode = '22023';
  end if;

  select workspace_id into v_workspace_id
  from public.kanban_boards
  where id=p_board_id and workspace_id=p_workspace_id
  for update;
  if not found then raise exception 'board_not_found' using errcode='P0002'; end if;
  if not kanban_private.has_workspace_role(p_workspace_id,array['owner','admin','editor','member']) then
    raise exception 'card_create_forbidden' using errcode='42501';
  end if;

  select * into v_column from public.kanban_columns
  where id=p_column_id and board_id=p_board_id and workspace_id=p_workspace_id and not is_archived;
  if not found then raise exception 'target_column_not_found' using errcode='P0002'; end if;

  if v_column.wip_limit is not null then
    select count(*) into v_count from public.kanban_cards
    where column_id=p_column_id and not is_archived;
    if v_count>=v_column.wip_limit then
      raise exception 'column_wip_limit_exceeded' using errcode='23514';
    end if;
  end if;

  select coalesce(max(position),0)+1000 into v_position
  from public.kanban_cards
  where board_id=p_board_id and column_id=p_column_id and not is_archived;

  insert into public.kanban_cards(
    workspace_id,board_id,column_id,title,description,priority,
    acceptance_criteria,due_date,position,metadata,created_by,updated_by
  ) values (
    p_workspace_id,p_board_id,p_column_id,trim(p_title),p_description,
    coalesce(p_priority,'medium'),p_acceptance_criteria,p_due_date,
    v_position,coalesce(p_metadata,'{}'::jsonb),auth.uid(),auth.uid()
  ) returning * into v_card;

  return to_jsonb(v_card);
end;
$$;
revoke all on function public.kanban_create_card(uuid,uuid,uuid,text,text,text,text,date,jsonb) from public,anon;
grant execute on function public.kanban_create_card(uuid,uuid,uuid,text,text,text,text,date,jsonb) to authenticated;

create or replace function public.kanban_move_card(
  p_card_id uuid,
  p_target_column_id uuid,
  p_expected_revision integer
)
returns jsonb
language plpgsql
security invoker
set search_path = pg_catalog,public,kanban_private,auth
as $$
declare
  v_card public.kanban_cards;
  v_target public.kanban_columns;
  v_workspace_id uuid;
  v_board_id uuid;
  v_position numeric;
  v_count integer;
begin
  select workspace_id,board_id into v_workspace_id,v_board_id
  from public.kanban_cards where id=p_card_id;
  if not found then raise exception 'card_not_found' using errcode='P0002'; end if;

  perform 1 from public.kanban_boards
  where id=v_board_id and workspace_id=v_workspace_id
  for update;
  if not found then raise exception 'board_not_found' using errcode='P0002'; end if;
  if not kanban_private.has_workspace_role(v_workspace_id,array['owner','admin','editor','member']) then
    raise exception 'card_move_forbidden' using errcode='42501';
  end if;

  select * into v_card from public.kanban_cards where id=p_card_id for update;
  if v_card.revision<>p_expected_revision then
    raise exception 'revision_conflict' using errcode='40001';
  end if;
  if v_card.is_archived then raise exception 'card_archived' using errcode='55000'; end if;

  select * into v_target from public.kanban_columns
  where id=p_target_column_id and board_id=v_board_id and workspace_id=v_workspace_id and not is_archived;
  if not found then raise exception 'target_column_not_found' using errcode='P0002'; end if;

  if v_target.id<>v_card.column_id and v_target.wip_limit is not null then
    select count(*) into v_count from public.kanban_cards
    where column_id=p_target_column_id and not is_archived;
    if v_count>=v_target.wip_limit then
      raise exception 'column_wip_limit_exceeded' using errcode='23514';
    end if;
  end if;

  if v_target.id=v_card.column_id then
    return to_jsonb(v_card);
  end if;

  select coalesce(max(position),0)+1000 into v_position
  from public.kanban_cards
  where board_id=v_board_id and column_id=p_target_column_id and not is_archived;

  update public.kanban_cards
  set column_id=p_target_column_id,position=v_position,updated_by=auth.uid()
  where id=p_card_id
  returning * into v_card;
  return to_jsonb(v_card);
end;
$$;
revoke all on function public.kanban_move_card(uuid,uuid,integer) from public,anon;
grant execute on function public.kanban_move_card(uuid,uuid,integer) to authenticated;

comment on function public.kanban_create_card(uuid,uuid,uuid,text,text,text,text,date,jsonb) is
  'Creates a card atomically under a board lock, preserving column order and enforcing WIP limits.';
comment on function public.kanban_move_card(uuid,uuid,integer) is
  'Moves a card atomically under a board lock with expected-revision and WIP-limit checks.';
