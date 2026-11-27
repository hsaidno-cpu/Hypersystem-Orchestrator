-- Private artifact storage for PRE–RPEDS federated release verification.
-- Objects are written and read only by the service-role-backed pre-core-federation Edge Function.
-- No public bucket or end-user Storage policy is created.

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
select
  'pre-release-artifacts',
  'pre-release-artifacts',
  false,
  104857600,
  array['application/gzip', 'application/octet-stream']::text[]
where not exists (
  select 1 from storage.buckets where id = 'pre-release-artifacts'
);

do $$
begin
  if exists (
    select 1 from storage.buckets
    where id = 'pre-release-artifacts' and public = true
  ) then
    raise exception 'pre-release-artifacts bucket must remain private';
  end if;
end
$$;
