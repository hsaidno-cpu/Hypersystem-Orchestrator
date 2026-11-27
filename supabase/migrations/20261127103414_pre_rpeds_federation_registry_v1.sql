-- PRE-RPEDS federation registry.
create table if not exists public.pre_kernel_releases (
 id uuid primary key default gen_random_uuid(),
 event_id text not null unique,
 idempotency_key text not null unique,
 canonical_identity text not null check (canonical_identity='pre-rpeds-shared-roadmap-dna'),
 release_version text not null, release_id text not null, source_locator text not null,
 artifact_sha256 text not null check (artifact_sha256 ~ '^[a-f0-9]{64}$'),
 contract_version text not null, compatibility_range text not null,
 release_channel text not null check (release_channel in ('stable','candidate','preview')),
 issuer_identity text not null, issuer_key_id text not null,
 signature_verified boolean not null default false,
 origin_lineage jsonb not null default '[]'::jsonb,
 capability_classes jsonb not null default '[]'::jsonb,
 payload jsonb not null default '{}'::jsonb,
 processing_state text not null default 'RECEIVED'
  check (processing_state in ('RECEIVED','VALIDATED','REJECTED','QUARANTINED','REVOKED','SUPERSEDED')),
 received_at timestamptz not null default now(), issued_at timestamptz not null,
 processed_at timestamptz, last_error text, created_at timestamptz not null default now()
);
create index if not exists pre_kernel_releases_version_idx on public.pre_kernel_releases (release_version desc, received_at desc);
create index if not exists pre_kernel_releases_state_idx on public.pre_kernel_releases (processing_state, received_at desc);

create table if not exists public.pre_host_subscriptions (
 host_id text primary key, host_name text not null, manifestation text not null,
 host_role text not null check (host_role in ('PRODUCER','CONSUMER','BOTH','REGISTRY')),
 repository_url text, enabled boolean not null default true,
 subscribed_channel text not null default 'stable' check (subscribed_channel in ('stable','candidate','preview','all')),
 current_kernel_version text, current_release_id text, supported_kernel_range text not null default '*',
 adapter_version text, policy_profile_ref text,
 policy_profile_status text not null default 'PENDING_PROFILE'
  check (policy_profile_status in ('VERIFIED','PENDING_REVIEW','PENDING_PROFILE','REJECTED')),
 auto_adopt_nonbreaking boolean not null default false,
 required_checks jsonb not null default '[]'::jsonb, sync_state text not null default 'NOT_CONFIGURED',
 last_event_at timestamptz, last_adopted_at timestamptz, updated_at timestamptz not null default now()
);

create table if not exists public.pre_host_adoption_receipts (
 id uuid primary key default gen_random_uuid(),
 event_id text not null references public.pre_kernel_releases(event_id) on delete restrict,
 host_id text not null references public.pre_host_subscriptions(host_id) on delete restrict,
 previous_kernel_version text, candidate_kernel_version text not null,
 artifact_sha256 text not null check (artifact_sha256 ~ '^[a-f0-9]{64}$'),
 adapter_version text,
 adapter_disposition text not null check (adapter_disposition in ('DIRECT_COMPATIBLE','ADAPTED_COMPATIBLE','HELD_FOR_AUTHORITY','QUARANTINED_OR_REJECTED','NOT_ASSESSED')),
 policy_refs jsonb not null default '[]'::jsonb, approval_refs jsonb not null default '[]'::jsonb,
 test_results jsonb not null default '[]'::jsonb,
 adoption_state text not null default 'PENDING_ADAPTER'
  check (adoption_state in ('PENDING_ADAPTER','QUEUED_FOR_TESTS','PR_OPENED','APPROVAL_PENDING','ADOPTED','VERIFIED','HELD','QUARANTINED','REJECTED','RETRY_PENDING','DEAD_LETTER','ROLLED_BACK','REVOKED')),
 pull_request_ref text, commit_ref text, deployment_ref text, readback_version text, readback_digest text,
 rollback_ref text, reason text, residual_risks jsonb not null default '[]'::jsonb,
 receipt_payload jsonb not null default '{}'::jsonb, observed_at timestamptz not null default now(),
 unique(event_id, host_id)
);
create index if not exists pre_host_adoption_host_state_idx on public.pre_host_adoption_receipts (host_id, adoption_state, observed_at desc);

create table if not exists public.pre_capability_contributions (
 id uuid primary key default gen_random_uuid(),
 contribution_id text not null unique,
 contributor_host text not null references public.pre_host_subscriptions(host_id) on delete restrict,
 contribution_class text not null check (contribution_class in ('SHARED_DNA','HOST_EXTENSION','HOST_ADAPTATION','HOST_SPECIFIC','QUARANTINED_OR_REJECTED')),
 capability_name text not null, capability_version text not null, contract_version text not null,
 content_digest text not null check (content_digest ~ '^[a-f0-9]{64}$'),
 provenance jsonb not null default '{}'::jsonb, sanitized_summary text not null,
 license_or_reuse_basis text, validation_refs jsonb not null default '[]'::jsonb,
 approval_state text not null default 'PENDING' check (approval_state in ('PENDING','APPROVED','REJECTED','DEFERRED','REVOKED')),
 origin_lineage jsonb not null default '[]'::jsonb, created_at timestamptz not null default now(), reviewed_at timestamptz
);

alter table public.pre_kernel_releases enable row level security;
alter table public.pre_host_subscriptions enable row level security;
alter table public.pre_host_adoption_receipts enable row level security;
alter table public.pre_capability_contributions enable row level security;
revoke all on table public.pre_kernel_releases from anon, authenticated;
revoke all on table public.pre_host_subscriptions from anon, authenticated;
revoke all on table public.pre_host_adoption_receipts from anon, authenticated;
revoke all on table public.pre_capability_contributions from anon, authenticated;
grant all on table public.pre_kernel_releases to service_role;
grant all on table public.pre_host_subscriptions to service_role;
grant all on table public.pre_host_adoption_receipts to service_role;
grant all on table public.pre_capability_contributions to service_role;

insert into public.pre_host_subscriptions (
 host_id,host_name,manifestation,host_role,repository_url,subscribed_channel,current_kernel_version,current_release_id,
 supported_kernel_range,adapter_version,policy_profile_ref,policy_profile_status,auto_adopt_nonbreaking,required_checks,sync_state
) values
 ('pre-standalone','PRE Standalone','PRE_STANDALONE','BOTH',null,'stable','0.1.5','pluginrel_6b095bf2f4308191bf7d46ce98da36f7','>=0.1.0 <1.0.0','0.1.5','Plugin Creator USER/PRIVATE release; adapter profile pending','PENDING_PROFILE',false,'["source-readback","contract-tests","package-validation"]'::jsonb,'SOURCE_CURRENT'),
 ('asfree-rpeds','A.S.F.R.E.E / RPEDS','RPEDS_ASFREE','CONSUMER','https://github.com/hsaidno-cpu/A.S.F.R.E.E','stable',null,null,'>=0.1.0 <1.0.0','0.5.0-rc.1','https://github.com/hsaidno-cpu/A.S.F.R.E.E/pull/13','PENDING_REVIEW',false,'["afsa-policy","asfree-package-ci","rpeds-regression","readback","rollback"]'::jsonb,'SOURCE_PR_PENDING'),
 ('hsar','HSAR','HSAR_HOST','CONSUMER','https://github.com/hsaidno-cpu/Hypersystem-Orchestrator','stable',null,null,'>=0.1.0 <1.0.0',null,'docs/hsar/HSAR-REGISTRY-AND-OPERATING-CONTRACT.md','PENDING_PROFILE',false,'["hsar-routing","provenance","evidence-assurance","readback"]'::jsonb,'CONDITIONAL_ROUTING_ONLY'),
 ('hso','HSO Control Plane','HSO_REGISTRY','REGISTRY','https://github.com/hsaidno-cpu/Hypersystem-Orchestrator','stable',null,null,'>=0.1.0 <1.0.0',null,'catalog/hso-routing-policy.json','PENDING_REVIEW',false,'["catalog-validation","contract-validation","host-registry-readback"]'::jsonb,'CATALOG_SYNC_PENDING')
on conflict (host_id) do nothing;
