import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pickle
import os

def load_jsonl_data(file_path):
    """Load data from JSONL file."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def create_embeddings(texts, model_name='all-MiniLM-L6-v2'):
    """Create embeddings for the given texts using sentence-transformers."""
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings

def create_faiss_index(embeddings, dimension):
    """Create and return a FAISS index."""
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    return index

def save_index_and_metadata(index, metadata, output_dir):
    """Save FAISS index and metadata."""
    os.makedirs(output_dir, exist_ok=True)
    # Save FAISS index
    faiss.write_index(index, os.path.join(output_dir, 'faiss_index.bin'))
    # Save metadata
    with open(os.path.join(output_dir, 'metadata.pkl'), 'wb') as f:
        pickle.dump(metadata, f)

def main():
    # Configuration
    input_file = 'paragon_scraper/paragon_data.jsonl'
    output_dir = 'faiss_index'
    model_name = 'all-MiniLM-L6-v2'
    
    # Load data
    print("Loading data from JSONL...")
    data = load_jsonl_data(input_file)
    
    # Prepare texts for embedding
    texts = []
    metadata = []
    
    for item in data:
        # Combine title and content for better context
        text = f"{item.get('title', '')} {item.get('text_content', '')}"
        if text.strip():  # Only add non-empty texts
            texts.append(text)
            metadata.append({
                'url': item.get('url', ''),
                'title': item.get('title', ''),
                'text_content': item.get('text_content', ''),
                'timestamp': item.get('timestamp', '')
            })
    
    # Create embeddings
    print("Creating embeddings...")
    embeddings = create_embeddings(texts, model_name)
    
    # Create FAISS index
    print("Creating FAISS index...")
    dimension = embeddings.shape[1]
    index = create_faiss_index(embeddings, dimension)
    
    # Save index and metadata
    print("Saving index and metadata...")
    save_index_and_metadata(index, metadata, output_dir)
    
    print(f"Done! Index and metadata saved in {output_dir}/")

if __name__ == "__main__":
    main()