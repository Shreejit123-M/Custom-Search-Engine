"""
rag.py
Retrieval-Augmented Generation pipeline.

Flow:
  1. Run hybrid search to retrieve top-k relevant chunks
  2. Build a grounded context prompt from those chunks
  3. Call the LLM (Anthropic Claude via API, or OpenAI as fallback)
  4. Return the answer with source citations

Set environment variables:
  ANTHROPIC_API_KEY   for Claude
  OPENAI_API_KEY      for OpenAI (fallback)
"""

import os

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "")
RAG_TOP_K         = 5       # number of chunks to retrieve
MAX_TOKENS        = 800     # max LLM output tokens


SYSTEM_PROMPT = """You are a precise document assistant. Answer the user's question using ONLY the provided document context.

Rules:
- Base your answer strictly on the context below.
- If the context does not contain enough information, say "I couldn't find a clear answer in the uploaded documents."
- At the end of your answer, cite the source document(s) in the format: [Source: filename, chunk N].
- Be concise but complete. Use bullet points for lists.
"""


def build_context(search_results: list[dict]) -> str:
    parts = []
    for i, r in enumerate(search_results, 1):
        parts.append(
            f"--- Chunk {i} | Source: {r.get('filename','?')} ---\n{r.get('full_text') or r.get('text_preview','')}"
        )
    return "\n\n".join(parts)


def answer_with_rag(query: str, search_engine, top_k: int = RAG_TOP_K) -> dict:
    """
    Retrieve relevant chunks and generate a grounded answer.
    Returns dict: {answer, sources, search_results, llm_provider}
    """
    results = search_engine.search(query, top_k=top_k)

    # Enrich with full_text from index
    for r in results:
        stats = search_engine.index.document_stats.get(r["doc_id"], {})
        r["full_text"] = stats.get("full_text", r.get("text_preview", ""))

    if not results:
        return {
            "answer":   "No relevant documents found. Please upload documents first.",
            "sources":  [],
            "results":  [],
            "provider": "none",
        }

    context = build_context(results)
    user_msg = f"Context:\n{context}\n\nQuestion: {query}"

    sources = list({r["filename"] for r in results if r.get("filename")})

    # ── Try Anthropic Claude ──────────────────────────────────────────────────
    if ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            answer = response.content[0].text
            return {"answer": answer, "sources": sources, "results": results, "provider": "claude"}
        except Exception as e:
            print(f"[RAG] Anthropic error: {e}")

    # ── Try OpenAI ────────────────────────────────────────────────────────────
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=MAX_TOKENS,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_msg},
                ],
            )
            answer = response.choices[0].message.content
            return {"answer": answer, "sources": sources, "results": results, "provider": "openai"}
        except Exception as e:
            print(f"[RAG] OpenAI error: {e}")

    # ── Fallback: no LLM configured ───────────────────────────────────────────
    preview_lines = []
    for r in results[:3]:
        preview_lines.append(f"• [{r.get('filename','')}] {r.get('text_preview','')[:200]}")
    fallback = (
        "⚠️ No LLM API key configured. Showing raw retrieved chunks:\n\n"
        + "\n\n".join(preview_lines)
        + "\n\nTip: Set ANTHROPIC_API_KEY or OPENAI_API_KEY to enable AI-generated answers."
    )
    return {"answer": fallback, "sources": sources, "results": results, "provider": "fallback"}
