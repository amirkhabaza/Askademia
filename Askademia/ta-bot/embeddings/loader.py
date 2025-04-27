import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pathlib, fitz, tqdm, sys, glob
from embeddings.embedder         import embed
from embeddings.chunk_utils      import sliding_chunks as chunks
from db.mongo_client             import get_db
import argparse
import config # Import config to access CANVAS_COURSE_IDS

COLL = get_db()["syllabus_chunks"]          # Collection name
DB_INSERT_BATCH = 64                      # Mongo bulk-insert size

def pdf_text(path: pathlib.Path) -> str:
    """Return plain text from a PDF (PyMuPDF)."""
    return "".join(p.get_text("text") for p in fitz.open(path))

def ingest(pdf_path: pathlib.Path, course_id: str):
    """Processes a single PDF file and inserts its chunks into MongoDB."""
    text = pdf_text(pdf_path)
    buf  = []
    processed_chunks = 0

    for c in tqdm.tqdm(chunks(text), desc=f"Chunking {pdf_path.name}"):
        try:
            embedding = embed(c) 
            buf.append({"course_id": course_id,
                        "file":       pdf_path.name,
                        "chunk":      c,
                        "embedding":  embedding})
            
            if len(buf) == DB_INSERT_BATCH:
                COLL.insert_many(buf); 
                processed_chunks += len(buf)
                buf.clear()
        except Exception as e:
            print(f"\nError processing chunk for {pdf_path.name}: {e}. Skipping chunk.")

    if buf: 
        try:
            COLL.insert_many(buf) 
            processed_chunks += len(buf)
        except Exception as e:
            print(f"\nError inserting final batch for {pdf_path.name}: {e}")
            
    print(f"✅ {pdf_path.name}: Processed and attempted insert for {processed_chunks} chunks.")

# ── CLI ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load PDF documents from a course-specific folder into MongoDB.")
    parser.add_argument("course_name", type=str, 
                        help="The course name (key defined in config.CANVAS_COURSE_IDS) whose folder should be processed.")
    
    args = parser.parse_args()
    course_name_to_process = args.course_name

    # Validate course_name against config
    if course_name_to_process not in config.CANVAS_COURSE_IDS:
        print(f"Error: Course name '{course_name_to_process}' not found as a key in config.CANVAS_COURSE_IDS.")
        print(f"Available course names: {list(config.CANVAS_COURSE_IDS.keys())}")
        sys.exit(1)

    # Get the actual course ID from config
    target_course_id = config.CANVAS_COURSE_IDS[course_name_to_process]
    
    # --- Find PDFs in the course-specific directory --- 
    base_embedding_dir = "embeddings" # Assumes this script is run from project root usually
    course_folder_path = os.path.join(base_embedding_dir, course_name_to_process)
    
    if not os.path.isdir(course_folder_path):
        print(f"Error: Directory not found for course '{course_name_to_process}': {course_folder_path}")
        print("Did you run the download script first?" )
        sys.exit(1)

    pdf_files_to_process = list(pathlib.Path(course_folder_path).glob("*.pdf"))

    if not pdf_files_to_process:
        print(f"No PDF files found in directory: {course_folder_path}")
        sys.exit(0)

    print(f"Found {len(pdf_files_to_process)} PDF(s) in {course_folder_path} for course ID '{target_course_id}'")
    
    # --- Process each PDF found --- 
    for pdf_path in pdf_files_to_process:
        print(f"\nProcessing file: {pdf_path}...")
        ingest(pdf_path, target_course_id) # Pass the specific PDF path and the correct course ID

    print("\nDocument loading process finished.")
