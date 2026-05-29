# Noetfield GIE v3.1 — Cursor Master Build Prompt

Document key: `noetfield-gie-cursor-master-prompt-v31`

## Purpose

Production-ready `graph_inference_engine.py`: LangGraph pipeline with resolve_entities,
extract_direct_relations, perform_multi_hop_inference, calculate_strength_confidence,
update_knowledge_graph, propagate_inferences, final_reflection.

## Constraints

- Claude primary, Ollama fallback; Supabase + pgvector
- Min confidence 0.55; deterministic explainable JSON output
- Functions: run_full_inference, resolve_or_create_entity, upsert_relationship, get_graph_paths

## Registry

Implementation prompt for GIE module; normative spec is `noetfield-gie-specification-supplement-v31`.
