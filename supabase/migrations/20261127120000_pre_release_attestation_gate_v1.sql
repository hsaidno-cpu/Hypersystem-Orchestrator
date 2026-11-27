-- Separate publisher transport authentication from independent release attestation.
alter table public.pre_kernel_releases
  add column if not exists publisher_hmac_verified boolean not null default false,
  add column if not exists artifact_digest_verified boolean not null default false,
  add column if not exists issuer_signature_verified boolean not null default false,
  add column if not exists contract_validated boolean not null default false,
  add column if not exists source_commit text,
  add column if not exists publisher_run_ref text,
  add column if not exists verification_evidence jsonb not null default '{}'::jsonb;

alter table public.pre_kernel_releases
  drop constraint if exists pre_kernel_releases_processing_state_check;

alter table public.pre_kernel_releases
  add constraint pre_kernel_releases_processing_state_check
  check (processing_state in (
    'RECEIVED','PUBLISHER_AUTHENTICATED','RELEASED',
    'REJECTED','QUARANTINED','REVOKED','SUPERSEDED'
  ));

update public.pre_kernel_releases
set processing_state = 'PUBLISHER_AUTHENTICATED',
    publisher_hmac_verified = signature_verified,
    artifact_digest_verified = false,
    issuer_signature_verified = false,
    contract_validated = false
where processing_state = 'VALIDATED';
