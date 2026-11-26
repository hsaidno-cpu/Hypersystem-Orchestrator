# Candidate Repository Build Specifications

## Photo Fixer 1.0.0
Package ID plugins_6afeb1f444d081918e5e191e062b82ad · release pluginrel_6afeb1f735888191b1d25574f336661b · 19 files. Git candidate hsaidno-cpu/Photo-Fixer@95339901f84cdae861efcebd9820cb2e1efdc27d has README/LICENSE only.

Target layout:
```text
photo-fixer/
├── .codex-plugin/plugin.json
├── plugin.json
├── README.md
├── CHANGELOG.md
├── LICENSE-DECISION.md
├── THIRD-PARTY-NOTICES.md
├── skills/photo-fixer/SKILL.md
├── skills/photo-fixer/references/{command-catalog.md,original-100-commands.txt,output-presets.md,quality-checklist.md}
├── skills/photo-fixer-*/SKILL.md
├── tests/fixtures/
├── tests/test_manifest.py
├── tests/test_skill_links.py
├── tests/test_prompt_contract.py
├── tests/test_routing.py
├── tests/test_negative_triggers.py
└── .github/workflows/validate.yml
```

Acceptance: full 19-path hash inventory; preserve original-source trace; identity/face preservation tests; bounded restoration/upscaling claims; all specialist references resolve; positive/negative trigger tests; rights audit.

## PVEE Promkes Super Orchestrator 2.0.2
Package ID plugins_6b029d31109c8191b34f7d50723971cb · release pluginrel_6b029dfa21e88191957129cfce63353f · 37 files and 14 procedures. Git candidate CL-VAEPPC@1ab0c41081ccdbb91cc9dec0a2864acd0de00d54 is a 3-file V3.0 legacy shell, not 2.0.2.

Target layout:
```text
pvee-promkes-super-orchestrator/
├── .codex-plugin/plugin.json
├── plugin.json
├── README.md
├── CHANGELOG.md
├── LICENSE-DECISION.md
├── THIRD-PARTY-NOTICES.md
├── docs/{architecture-catalog.md,forensic-audit.md,octa-prompt-gap-matrix.md,progressive-evaluation-roadmap.md,source-design-review.md,acceptance-matrix.md}
├── skills/promkes-orchestrator/SKILL.md
├── skills/promkes-orchestrator/{references/,scripts/}
├── skills/promkes-*/SKILL.md
├── schemas/
├── tests/fixtures/
├── tests/test_fact_lock.py
├── tests/test_claim_evidence_links.py
├── tests/test_stage_gates.py
├── tests/test_state_recovery.py
├── tests/test_manifest_validation.py
└── .github/workflows/validate.yml
```

Acceptance: 37/37 package paths mapped; Fact Lock and claim-evidence tracing; stage gates; recovery; manifest semantics; independent QA; rights/privacy; human approval before health content release.

## Remote creation boundary
The connected GitHub actions support branch/tree/blob/file/commit on existing repos but do not expose repository creation or visibility settings. Existing candidates are public and the Plugin Creator packages are USER/PRIVATE. This PR intentionally does not push private package contents to either public repo. Create two private destinations using GitHub UI/API with repo-creation permission, then import the exact release under owner authority and compare all paths/hashes.
