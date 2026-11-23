# Cross-Platform Adapter Matrix

**Revision:** 1.0.0 — 23 November 2026.  
**Status:** Target architecture; no adapter is currently implemented or host-tested by this repository change.

## 1. Why adapters are required

The Hypersystem registry is platform-neutral, but host installation and runtime capabilities are not. Each platform adapter translates a canonical package and entitlement into the host's supported package, configuration, transport, authentication, namespace and lifecycle model.

MCP is the preferred common protocol for remote tools where supported. It is not a universal wrapper for all native agent skills, UI extensions, lifecycle hooks or platform-specific package formats.

## 2. Target matrix

| Target | Intended integration mode | Adapter state | Host activation | Runtime |
|---|---|---|---|---|
| ChatGPT | Remote MCP app/connector | PLANNED | NOT_RUN | NOT_RUN |
| Claude | Remote/local MCP where supported | PLANNED | NOT_RUN | NOT_RUN |
| Gemini CLI | Host MCP server configuration | PLANNED | NOT_RUN | NOT_RUN |
| VS Code / GitHub Copilot | Agent plugin bundle, MCP and/or skill package | PLANNED | NOT_RUN | NOT_RUN |
| Generic MCP host | Remote/local MCP | PLANNED | NOT_RUN | NOT_RUN |

The machine-readable source is catalog/platform-registry.json. Entries are implementation targets, not proof that any package is accepted by a host or available on a user's plan.

## 3. Required adapter contract

Every adapter implementation must publish adapter ID and semantic version; exact host product and tested version range; accepted package formats and transport modes; tool/resource/prompt mapping and collision policy; authentication, entitlement and authorization binding; host-specific permission and confirmation behavior; configuration schema and secret-reference convention; install, update, disable, uninstall and rollback behavior; logging/redaction and diagnostics; known feature gaps and capability negotiation; host activation and end-to-end runtime evidence.

## 4. Conformance gates

| Gate | Acceptance evidence |
|---|---|
| A0 — Adapter contract | Schema-valid adapter descriptor and explicit feature map |
| A1 — Package conversion | Canonical package converted without losing source, version, license or ownership metadata |
| A2 — Auth and policy | Authentication and least-privilege grants correctly map to host identities/scopes |
| A3 — Host activation | Exact named host/version can install/discover the intended package |
| A4 — Tool invocation | A real tool call returns a traceable output under the correct plugin identity |
| A5 — Lifecycle | Update, disable, uninstall and rollback behave correctly |
| A6 — Isolation | Unauthorized plugin/tool calls are denied; one module's failure does not affect another |

A passing CI schema test cannot be copied to A3-A6. Use NOT_RUN until evidence exists.

## 5. Host-specific implementation notes

### ChatGPT
Build a remote MCP adapter and document the required account/workspace capabilities. The adapter must not claim that copying a GitHub URL installs an app into a user's account. The user or workspace administrator must complete host-side connection and permission steps.

### Claude
Map the canonical plugin package to the MCP and/or native integration surfaces available in the exact Claude product/client version. Keep native and MCP capabilities explicit; do not assume feature parity.

### Gemini CLI
Generate host configuration only after confirming the installed CLI's supported transports, command format and allowlist controls. Keep credentials out of checked-in configuration.

### VS Code / GitHub Copilot
Where supported, create a host-specific plugin bundle that may reference skills and MCP servers. Preserve the canonical plugin keys and version locks. A Copilot plugin package is not a generic package for other platforms.

### Generic MCP-compatible hosts
Publish a minimal MCP endpoint and declare exact protocol, transport, authentication and capability support. Require a conformance suite per host because clients differ in tool discovery and UI behavior.

## 6. Adapter release checklist

- [ ] Adapter source and maintainer identified.
- [ ] Host/version support matrix pinned.
- [ ] Canonical package and artifact hashes verified.
- [ ] License and redistribution rights cleared.
- [ ] Authentication and authorization tests pass.
- [ ] Host activation test passes.
- [ ] Runtime invocation and output read-back pass.
- [ ] Update, disable, uninstall and rollback pass.
- [ ] Security, redaction and isolation review passes.
- [ ] Adapter status updated only with evidence.
