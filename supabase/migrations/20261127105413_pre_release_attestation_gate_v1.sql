-- PRE–RPEDS release attestation gate.
-- Mirrors the live Supabase migration version 20261127105413.
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
  check (processing_state = any (array[
    'RECEIVED','PUBLISHER_AUTHENTICATED','RELEASED','REJECTED',
    'QUARANTINED','REVOKED','SUPERSEDED'
  ]::text[]));

create index if not exists pre_kernel_releases_attested_state_idx
  on public.pre_kernel_releases (
    processing_state, artifact_digest_verified, issuer_signature_verified,
    contract_validated, received_at desc
  );
