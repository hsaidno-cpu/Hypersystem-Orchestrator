# Cross-Platform Adapter Matrix

**Version:** 1.0.0 — 23 November 2026.  
**Status:** Platform targets only; no adapter is currently implemented or host-tested by this change.

## Purpose

The Hypersystem registry is platform-neutral; host installation and runtime capabilities are not. Each adapter translates canonical packages and entitlements into the host's package, configuration, transport, authentication, namespace and lifecycle model.

MCP is a common remote tool transport where supported. It is not a universal wrapper for native skills, UI extensions, hooks or platform-specific packages.

## Target matrix

| Target | Intended mode | Adapter | Host activation | Runtime |
|---|---|---|---|---|
| ChatGPT | Remote MCP app/connector | PLANNED | NOT_RUN | NOT_RUN |
| Claude | Remote/local MCP where supported | PLANNED | NOT_RUN | NOT_RUN |
| Gemini CLI | Host MCP configuration | PLANNED | NOT_RUN | NOT_RUN |
| VS Code / GitHub Copilot | Agent plugin bundle, MCP and/or skill package | PLANNED | NOT_RUN | NOT_RUN |
| Generic MCP host | Remote/local MCP | PLANNED | NOT_RUN | NOT_RUN |

The machine-readable registry is catalog/platform-registry.json. Registration is not proof of host acceptance or user-plan availability.

## Required adapter contract

Every adapter publishes adapter ID/version; exact host/version range; accepted formats and transports; tool/resource/prompt mapping; authentication, entitlement and authorization binding; permission/confirmation behavior; config schema and secret reference convention; install/update/disable/uninstall/rollback; logs and diagnostics; feature gaps; host activation and end-to-end runtime evidence.

## Conformance gates

| Gate | Evidence |
|---|---|
| A0 Adapter contract | Schema-valid descriptor and feature map |
| A1 Package conversion | Source/version/license/ownership metadata preserved |
| A2 Auth and policy | Least-privilege mapping to host identity and scopes |
| A3 Host activation | Named host/version installs and discovers intended package |
| A4 Tool invocation | Real call returns traceable output under correct plugin identity |
| A5 Lifecycle | Update, disable, uninstall and rollback |
| A6 Isolation | Unauthorized calls denied; one module failure does not affect others |

CI schema success cannot be reused as A3-A6 proof. Keep NOT_RUN until evidence exists.

## Host-specific implementation notes

### ChatGPT
Build a remote MCP adapter and document account/workspace requirements. Copying a GitHub URL does not install an app into an account. The user or workspace administrator completes host-side connection and permission steps.

### Claude
Map to MCP and/or native integration surfaces supported by the exact product/client version. Keep native and MCP capability claims separate.

### Gemini CLI
Generate host configuration only after validating the installed CLI's transport, command format, allowlists and exclusions. Keep credentials out of checked-in config.

### VS Code / GitHub Copilot
Where supported, package skills and MCP server declarations into a host-specific plugin bundle. Preserve canonical plugin keys and version locks. This is not a generic cross-platform package.

### Generic MCP host
Publish exact protocol, transport, auth and capability support. Require conformance testing for each host because clients differ in discovery, UI and permissions.

## Adapter release checklist

- [ ] Adapter source and maintainer identified.
- [ ] Host/version support pinned.
- [ ] Canonical package and artifact hashes verified.
- [ ] License and redistribution rights cleared.
- [ ] Authentication/authorization tests pass.
- [ ] Host activation and runtime invocation pass.
- [ ] Update, disable, uninstall and rollback pass.
- [ ] Security, redaction and isolation review passes.
- [ ] Registry status updated only with evidence.
