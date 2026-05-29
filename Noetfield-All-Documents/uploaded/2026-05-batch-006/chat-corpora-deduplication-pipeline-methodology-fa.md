# Chat Corpora Deduplication Pipeline (Methodology)

Document key: `chat-corpora-deduplication-pipeline-methodology-fa`

## Pipeline stages

1. Ingestion and parsing to unified Markdown/JSON
2. Semantic clustering via embeddings
3. Dedup merge and `[CONTRADICTION_FLAG]` reasoning pass
4. Structured output to relational DB, Notion, or Obsidian

## Tools referenced

AnythingLLM, Open WebUI, Flowise, Fabric CLI, custom Python + Pydantic structured outputs.

## Registry

Methodology reference for future chat-archive ingestion; not Noetfield runtime SOT.
