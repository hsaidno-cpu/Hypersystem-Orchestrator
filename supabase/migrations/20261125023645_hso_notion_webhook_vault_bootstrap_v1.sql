-- Bootstrap Notion webhook verification through encrypted Supabase Vault storage.
-- The initial Notion verification POST carries the token in its JSON body and is
-- intentionally not signed. The stored token is used to verify all later HMAC events.

create or replace function public.hso_register_notion_webhook_verification_token(p_token text)
returns boolean
language plpgsql
security invoker
set search_path = ''
as $$
declare
  existing_token text;
begin
  if p_token is null or length(p_token) < 16 or length(p_token) > 512 then
    raise exception 'invalid_notion_webhook_verification_token'
      using errcode = '22023';
  end if;

  select ds.decrypted_secret
    into existing_token
    from vault.decrypted_secrets as ds
   where ds.name = 'hso_notion_webhook_verification_token'
   order by ds.created_at desc
   limit 1;

  if existing_token is null then
    perform vault.create_secret(
      p_token,
      'hso_notion_webhook_verification_token',
      'Notion webhook verification token; captured by hso-notion-webhook bootstrap'
    );
    return true;
  end if;

  if existing_token = p_token then
    return false;
  end if;

  raise exception 'notion_webhook_verification_token_already_registered; owner rotation is required'
    using errcode = '23505';
end;
$$;

create or replace function public.hso_get_notion_webhook_verification_token()
returns text
language sql
security invoker
set search_path = ''
as $$
  select ds.decrypted_secret
    from vault.decrypted_secrets as ds
   where ds.name = 'hso_notion_webhook_verification_token'
   order by ds.created_at desc
   limit 1;
$$;

revoke all on function public.hso_register_notion_webhook_verification_token(text)
  from public, anon, authenticated;
revoke all on function public.hso_get_notion_webhook_verification_token()
  from public, anon, authenticated;
grant execute on function public.hso_register_notion_webhook_verification_token(text)
  to service_role;
grant execute on function public.hso_get_notion_webhook_verification_token()
  to service_role;

comment on function public.hso_register_notion_webhook_verification_token(text) is
  'Accepts a single Notion verification challenge token and stores it once in Supabase Vault. Only service_role may execute.';
comment on function public.hso_get_notion_webhook_verification_token() is
  'Returns the Notion webhook verification token to trusted Edge Functions only. Only service_role may execute.';
