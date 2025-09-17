### Design (Financial RAG System)

## Chunking strategy

- Sentence-aware chunking using regex split on end punctuation.
- Target chunk size ~800 tokens (by word count proxy) with 100-word overlap to preserve context across boundaries.
- Reasoning: balances retrieval granularity and context completeness while keeping embedding costs low.

## Embedding model choice

- `sentence-transformers` (default `all-MiniLM-L6-v2`).
- Pros: small, fast, strong semantic retrieval baseline; widely used; CPU-friendly.
- Retrieval uses FAISS `IndexFlatIP` with L2-normalized vectors to approximate cosine similarity.

## Agent / query decomposition

- Heuristic gate detects complex prompts (keywords like "compare", "across companies", "which is highest").
- For complex prompts, we ask the LLM (Groq `llama-3.1-8b-instant`) to produce specific sub-queries (one per company/metric), then retrieve per sub-query, and synthesize a final answer over aggregated context.
- For simple prompts, perform a single retrieval + short-generation pass.

## Interesting challenges / decisions

- SEC data reliability: falls back to realistic demo content in `sec_data/` to avoid brittle scraping and rate limits, ensuring reproducible demos.
- Model deprecation: switched from `llama3-8b-8192` to `llama-3.1-8b-instant` due to deprecation.
- API key handling: removed hardcoded key; uses `GROQ_API_KEY` env var.
- Context length: truncates aggregated context to avoid exceeding token limits, while maintaining most relevant snippets.
