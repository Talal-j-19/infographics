import os
import requests
from bs4 import BeautifulSoup
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle

# Config
BASE_URL = "https://docs.manim.community/en/stable/"
REFERENCE_PAGE = BASE_URL + "reference.html"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
EMBED_MODEL = "all-MiniLM-L6-v2"
OUTPUT_DIR = "./manim_rag_db"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Step 1: Scrape documentation links
def fetch_doc_links():
    page = requests.get(REFERENCE_PAGE)
    soup = BeautifulSoup(page.content, 'html.parser')
    links = [a['href'] for a in soup.select('a.reference.internal') if a['href'].endswith(".html")]
    full_links = [BASE_URL + href for href in links]
    return list(set(full_links))

# Step 2: Download and clean each page
def fetch_and_clean(url):
    try:
        content = requests.get(url).text
        soup = BeautifulSoup(content, 'html.parser')
        doc = soup.select_one("article#furo-main-content")
        if not doc:
            doc = soup.select_one("div.body")
        if not doc:
            doc = soup.select_one("div.document")
        if doc:
            return doc.get_text(separator="\n", strip=True)
    except Exception as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
    return None

# Step 3: Chunk text

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    if size <= overlap:
        raise ValueError("CHUNK_SIZE must be greater than CHUNK_OVERLAP")
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i+size])
        chunks.append(chunk)
    return chunks

# Step 4: Build and save FAISS index
def build_faiss_index(chunks, metadata, model_name=EMBED_MODEL):
    # Filter out empty chunks and corresponding metadata
    filtered = [(c, m) for c, m in zip(chunks, metadata) if c.strip()]
    if not filtered:
        print("[ERROR] No non-empty chunks to index.")
        return
    chunks, metadata = zip(*filtered)
    model = SentenceTransformer(model_name)
    print("[INFO] Generating embeddings...")
    embeddings = model.encode(list(chunks), show_progress_bar=True)
    if embeddings.shape[0] == 0:
        print("[ERROR] No embeddings generated. Exiting.")
        return

    print("[INFO] Building FAISS index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    # Save index and metadata
    faiss.write_index(index, os.path.join(OUTPUT_DIR, "manim_faiss.index"))
    with open(os.path.join(OUTPUT_DIR, "manim_chunks.pkl"), "wb") as f:
        pickle.dump(list(chunks), f)
    with open(os.path.join(OUTPUT_DIR, "manim_metadata.pkl"), "wb") as f:
        pickle.dump(list(metadata), f)

    print(f"[DONE] Saved {len(chunks)} chunks to {OUTPUT_DIR}")

# 🔧 Main process
def main():
    print("[INFO] Fetching documentation links...")
    links = fetch_doc_links()
    all_chunks = []
    all_metadata = []

    print(f"[INFO] Found {len(links)} pages. Processing...")
    for link in links:
        text = fetch_and_clean(link)
        if not text:
            print(f"[DEBUG] No text fetched for {link}")
            continue
        print(f"[DEBUG] Text length for {link}: {len(text)}")
        print(f"[DEBUG] Sample text: {text[:200]!r}")
        chunks = chunk_text(text)
        print(f"[DEBUG] Number of chunks for {link}: {len(chunks)}")
        all_chunks.extend(chunks)
        all_metadata.extend([link] * len(chunks))

    build_faiss_index(all_chunks, all_metadata)

if __name__ == "__main__":
    main()
