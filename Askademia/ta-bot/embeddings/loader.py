import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pathlib, fitz, tqdm, sys, glob
from embeddings.embedder         import embed
from embeddings.chunk_utils      import sliding_chunks as chunks
from db.mongo_client             import get_db

COLL = get_db()["syllabus_chunks"]          # or "syllabus_chunks"
BATCH = 64                                # Mongo bulk-insert size

def pdf_text(path: pathlib.Path) -> str:
    """Return plain text from a PDF (PyMuPDF)."""
    return "".join(p.get_text("text") for p in fitz.open(path))

def ingest(pdf: str | pathlib.Path, course_id: str = "GEN"):
    p    = pathlib.Path(pdf)
    text = pdf_text(p)
    buf  = []

    for c in tqdm.tqdm(chunks(text)):            # token-window splitter
        buf.append({"course_id": course_id,
                    "file":       p.name,
                    "chunk":      c,
                    "embedding":  embed(c)})
        if len(buf) == BATCH:
            COLL.insert_many(buf); buf.clear()

    if buf: COLL.insert_many(buf)                # flush leftovers
    print(f"✅ {p.name}: {COLL.count_documents({'file': p.name})} chunks")

# ── CLI ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Usage:  python embeddings/loader.py *.pdf COURSE_ID
    pdfs      = sys.argv[1:-1] or glob.glob("*.pdf")
    course_id = sys.argv[-1]   if len(sys.argv) > 2 else "GEN"
    for pdf in pdfs:
        ingest(pdf, course_id)
