alter table public.pre_host_subscriptions
 add column if not exists host_auth_secret_ref text,
 add column if not exists host_auth_status text not null default 'NOT_CONFIGURED'
  check (host_auth_status in ('CONFIGURED','NOT_CONFIGURED','ROTATION_REQUIRED'));
update public.pre_host_subscriptions
 set host_auth_secret_ref = case host_id
  when 'pre-standalone' then 'PRE_HOST_TOKEN_PRE_STANDALONE'
  when 'asfree-rpeds' then 'PRE_HOST_TOKEN_ASFREE_RPEDS'
  when 'hsar' then 'PRE_HOST_TOKEN_HSAR'
  when 'hso' then 'PRE_HOST_TOKEN_HSO'
  else host_auth_secret_ref end
 where host_auth_secret_ref is null;
update public.pre_host_subscriptions
 set host_auth_status='NOT_CONFIGURED'
 where host_auth_secret_ref is not null and host_auth_status <> 'CONFIGURED';
