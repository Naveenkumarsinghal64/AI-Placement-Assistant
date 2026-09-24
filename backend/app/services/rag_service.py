import uuid
from datetime import datetime
from pathlib import Path

import chromadb

from app.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DOCUMENT_UPLOADS_DIR,
    RETRIEVAL_TOP_K,
    VECTORSTORE_DIR,
)
from app.services import ai_service
from app.services.document_service import chunk_text
from app.services.text_extraction import extract_text

_client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
_collection = _client.get_or_create_collection(name="placement_documents")

ANSWER_PROMPT = """You are the AI Placement Assistant. Answer the student's question using ONLY the context below.

If the context does not contain enough information to answer confidently, say so clearly instead of guessing.

Context:
\"\"\"
{context}
\"\"\"

Question: {question}

Answer concisely and reference specific details from the context where relevant.
"""


def ingest_document(file_path: Path, original_filename: str) -> dict:
    text = extract_text(file_path)
    if not text.strip():
        raise ValueError("No readable text found in the uploaded document.")

    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    if not chunks:
        raise ValueError("Document produced no usable text chunks.")

    document_id = str(uuid.uuid4())
    uploaded_at = datetime.utcnow().isoformat()

    ids = [f"{document_id}-{i}" for i in range(len(chunks))]
    embeddings = [ai_service.embed_text(chunk) for chunk in chunks]
    metadatas = [
        {
            "document_id": document_id,
            "filename": original_filename,
            "chunk_index": i,
            "uploaded_at": uploaded_at,
        }
        for i in range(len(chunks))
    ]

    _collection.add(
        ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas
    )

    return {
        "id": document_id,
        "filename": original_filename,
        "chunk_count": len(chunks),
        "uploaded_at": uploaded_at,
    }


def list_documents() -> list[dict]:
    records = _collection.get(include=["metadatas"])
    seen: dict[str, dict] = {}
    for metadata in records["metadatas"]:
        doc_id = metadata["document_id"]
        if doc_id not in seen:
            seen[doc_id] = {
                "id": doc_id,
                "filename": metadata["filename"],
                "uploaded_at": metadata["uploaded_at"],
                "chunk_count": 0,
            }
        seen[doc_id]["chunk_count"] += 1
    return sorted(seen.values(), key=lambda d: d["uploaded_at"], reverse=True)


def delete_document(document_id: str) -> bool:
    existing = _collection.get(where={"document_id": document_id})
    if not existing["ids"]:
        return False
    _collection.delete(where={"document_id": document_id})
    return True


def answer_question(question: str) -> dict:
    if _collection.count() == 0:
        return {
            "answer": "No documents have been uploaded yet. Upload a placement "
            "document first so I can answer questions about it.",
            "sources": [],
        }

    query_embedding = ai_service.embed_text(question, task_type="retrieval_query")
    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=min(RETRIEVAL_TOP_K, _collection.count()),
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    if not documents:
        return {
            "answer": "I could not find relevant information in the uploaded documents.",
            "sources": [],
        }

    context = "\n\n---\n\n".join(
        f"[{meta['filename']}]: {doc}" for doc, meta in zip(documents, metadatas)
    )

    prompt = ANSWER_PROMPT.format(context=context, question=question)
    answer = ai_service.generate_text(prompt)

    sources = [
        {"document": meta["filename"], "snippet": doc[:200]}
        for doc, meta in zip(documents, metadatas)
    ]

    return {"answer": answer, "sources": sources}
