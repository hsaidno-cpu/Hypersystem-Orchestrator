---
name: context-integrity-auditor
description: Use when reviewing RAG, vector retrieval, memory, long conversations, multimodal inputs, transformations, summaries, or cross-agent handoffs for context and provenance integrity risks.
---
# Context Integrity Auditor

## Objective
Audit whether trust labels, provenance, semantic intent and authorization survive every transformation and persistence boundary.

## Surfaces
- RAG ingestion, chunking, embedding, indexing, ranking, filtering and citation.
- Persistent and episodic memory, summaries, profile facts and session state.
- OCR and image interpretation; audio transcription and speaker attribution; video frames, subtitles and metadata.
- Translation, paraphrase, encoding/decoding, normalization, extraction and summarization.
- Long-context truncation, recency/position effects and multi-turn state.
- Agent-to-agent messages, delegated tasks, tool outputs and workflow queues.

## Audit procedure
1. Inventory source, owner, trust class, sensitivity, retention and permitted use.
2. Trace source-to-output lineage, including transformations and storage.
3. Check whether untrusted instructions become imperative summaries or lose quotation/source labels.
4. Check retrieval poisoning, corpus contamination, stale documents, duplicate sources, ranking manipulation and citation mismatch.
5. Check memory write permissions, provenance, expiry, correction/deletion, user confirmation and conflict resolution.
6. Check modality-specific extraction uncertainty; distinguish OCR/transcription confidence from semantic truth.
7. Check cross-agent trust contracts: schema, sender identity, task scope, provenance, allowed actions and validation.
8. Test whether transformed content changes meaning or reconstructs restricted output. Assess end-to-end semantics, not only intermediate steps.
9. Recommend provenance-preserving schemas, source labels, scoped memory writes, retrieval filters, quote boundaries, validation and human review where needed.

## Output
Data lineage map; trust-label loss points; memory/RAG/multimodal findings; cross-agent handoff risks; testable controls; unresolved provenance and retention questions.

## Guardrails
Do not infer the contents of unseen modalities or stores. Do not claim that a source is poisoned without evidence. Use synthetic data for testing and avoid exposing personal or secret content unnecessarily.
