# embeddings/loader.py  ─────────────────────────────────────────
import pathlib, fitz, tqdm, os, sys
from embeddings.embedder        import embed
from embeddings.chunk_utils     import sliding_chunks as chunks  # token-based
from db.mongo_client            import get_db

COLLECTION = "syllabus_chunks"           # or course_chunks if you prefer
DB  = get_db()[COLLECTION]               # ↳ atlas.collection

def pdf_text(path: pathlib.Path) -> str:
    """Extract plain text from a PDF file."""
    doc = fitz.open(path)
    return "".join(page.get_text("text") for page in doc)

def ingest(pdf_path: str | pathlib.Path, course_id: str = "GEN"):
    path  = pathlib.Path(pdf_path)
    text  = pdf_text(path)
    batch = []

    for chunk in tqdm.tqdm(chunks(text, max_tokens=800, overlap=80)):
        batch.append({
            "course_id":  course_id,
            "file":       path.name,
            "chunk":      chunk,
            "embedding":  embed(chunk)
        })
        if len(batch) == 64:                       # ← tune batch size
            DB.insert_many(batch); batch.clear()

    if batch:                                     # flush leftovers
        DB.insert_many(batch)

    print(f"✅ {path.name}: now {DB.count_documents({'file': path.name})} chunks")

# -----------------------------------------------------------------
if __name__ == "__main__":
    # run:  python embeddings/loader.py syllabus.pdf DATA230
    pdfs = sys.argv[1:-1] or ["syllabus.pdf"]
    course = sys.argv[-1] if len(sys.argv) > 2 else "GEN"
    for pdf in pdfs: ingest(pdf, course)
