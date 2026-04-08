"""
app.py
Main Flask application.

Routes:
  GET  /                  → UI
  POST /upload            → Upload & index a document
  POST /search            → BM25/hybrid search
  POST /ask               → RAG Q&A
  GET  /documents         → List indexed files
  DELETE /documents/<fn>  → Remove a file
  GET  /stats             → Index statistics
"""

import os
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

from text_processor  import TextProcessor
from inverted_index  import InvertedIndex
from search_engine   import SearchEngine
from indexer         import index_document, remove_document_by_filename, list_indexed_files
from rag             import answer_with_rag

# ── Config ────────────────────────────────────────────────────────────────────
UPLOAD_FOLDER   = "uploads"
INDEX_PATH      = "data/index.json"
EMBED_PATH      = "data/embeddings.json"
ALLOWED_EXT     = {"pdf", "docx", "doc", "txt"}
MAX_FILE_MB     = 20

app = Flask(__name__)
app.config["UPLOAD_FOLDER"]      = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_MB * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("data",        exist_ok=True)

# ── Initialise core components ────────────────────────────────────────────────
text_proc = TextProcessor()
inv_index = InvertedIndex()
inv_index.load(INDEX_PATH)

search_eng = SearchEngine(inv_index, text_proc, embed_path=EMBED_PATH)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def save_index():
    inv_index.save(INDEX_PATH)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html",
                           semantic_enabled=search_eng.semantic_enabled)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"Unsupported format. Allowed: {', '.join(ALLOWED_EXT)}"}), 400

    filename  = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    result = index_document(save_path, inv_index, text_proc, search_eng)
    if "error" in result:
        return jsonify(result), 422

    save_index()
    return jsonify({
        "message":  f"✓ Indexed '{filename}' into {result['chunks']} chunk(s).",
        "filename": filename,
        "chunks":   result["chunks"],
        "chars":    result["char_count"],
    })


@app.route("/search", methods=["POST"])
def search():
    data  = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()
    top_k = int(data.get("top_k", 10))

    if not query:
        return jsonify({"error": "Query is empty"}), 400

    results = search_eng.search(query, top_k=top_k)
    return jsonify({
        "query":        query,
        "total":        len(results),
        "results":      results,
        "search_type":  results[0]["search_type"] if results else "none",
    })


@app.route("/ask", methods=["POST"])
def ask():
    data  = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"error": "Question is empty"}), 400

    response = answer_with_rag(query, search_eng)
    return jsonify(response)


@app.route("/documents", methods=["GET"])
def documents():
    files = list_indexed_files(inv_index)
    return jsonify({"files": files, "total": len(files)})


@app.route("/documents/<path:filename>", methods=["DELETE"])
def delete_document(filename):
    removed = remove_document_by_filename(filename, inv_index, search_eng)
    if removed == 0:
        return jsonify({"error": "File not found in index"}), 404

    # Remove from uploads folder too
    fpath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if os.path.exists(fpath):
        os.remove(fpath)

    save_index()
    return jsonify({"message": f"Removed '{filename}' ({removed} chunks).", "removed": removed})


@app.route("/stats", methods=["GET"])
def stats():
    files = list_indexed_files(inv_index)
    ft_counts: dict[str, int] = {}
    for f in files:
        ft_counts[f["filetype"]] = ft_counts.get(f["filetype"], 0) + 1

    return jsonify({
        "total_files":    len(files),
        "total_chunks":   inv_index.total_docs,
        "total_terms":    len(inv_index.index),
        "filetype_dist":  ft_counts,
        "semantic_on":    search_eng.semantic_enabled,
        "embeddings":     len(search_eng.embeddings),
    })


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
