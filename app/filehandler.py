# filehandler.py

import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter
from sentence_transformers import SentenceTransformer
from dao.classes import ClassDAO
from dao.syllabus import SyllabusDAO
import re


def clean_syllabus_text(text: str) -> str:

    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    text = re.sub(r'(\d)(\d{2,})%', r'\2%', text)
    text = re.sub(r' +', ' ', text)

    text = re.sub(r'\n{3,}', '\n\n', text)

    text = re.sub(r' *\n *', '\n', text)

    return text.strip()

print("Starting FINAL ingestion...\n")

model = SentenceTransformer("all-mpnet-base-v2")
syllabus_dao = SyllabusDAO()
class_dao = ClassDAO()

# ------------------ TEXT SPLITTERS ------------------
char_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""],
    chunk_size=600,
    chunk_overlap=150,
    length_function=len,
    is_separator_regex=False,

)

token_splitter = SentenceTransformersTokenTextSplitter(
    tokens_per_chunk=384,
    chunk_overlap=100
)

folder = "SyllabusFolder"
total_inserted = 0

# Load class table mapping
with class_dao.conn.cursor() as cur:
    cur.execute("SELECT cid, cname, ccode FROM class")
    course_map = {(row[1].upper(), row[2]): row[0] for row in cur.fetchall()}

print(f"Loaded {len(course_map)} courses\n")

# ------------------ PROCESS ALL PDFs ------------------
for filename in os.listdir(folder):
    if not filename.lower().endswith(".pdf"):
        continue

    parts = filename.split("-", 2)
    if len(parts) < 2:
        print(f"Skipping {filename} (invalid name format)\n")
        continue

    cname = parts[0].strip().upper()
    ccode = parts[1].strip()
    courseid = course_map.get((cname, ccode))

    if not courseid:
        print(f"NOT FOUND → {cname} {ccode} → skipping\n")
        continue

    print(f"Processing {filename} → {cname} {ccode} (cid={courseid})")

    try:
        reader = PdfReader(os.path.join(folder, filename))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

        if not text.strip():
            print(" → PDF text empty, skipping\n")
            continue

        # Split into chunks
        text = clean_syllabus_text(text)

        char_chunks = char_splitter.split_text(text)

        final_chunks = []
        for chunk in char_chunks:
            sub_chunks = token_splitter.split_text(chunk)
            final_chunks.extend(sub_chunks)

        final_chunks = [c for c in final_chunks if c.strip()]

        embeddings = model.encode(final_chunks)

        # Insert chunks into DB
        for chunk, emb in zip(final_chunks, embeddings):
            syllabus_dao.insert_chunk(courseid, chunk, emb.tolist())

        print(f" → Inserted {len(final_chunks)} chunks\n")
        total_inserted += len(final_chunks)

    except Exception as e:
        print(f"Error: {e}\n")

print("=" * 70)
print("INGESTION COMPLETE!")
print(f"Total chunks inserted: {total_inserted}")
print("=" * 70)
