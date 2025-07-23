from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import faiss
from typing import List, Optional
import uvicorn
import pickle
import os
from sentence_transformers import SentenceTransformer
from contextlib import asynccontextmanager

# Define startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load resources
    global index, metadata, model
    INDEX_DIR = 'faiss_index'
    index = faiss.read_index(os.path.join(INDEX_DIR, 'faiss_index.bin'))
    with open(os.path.join(INDEX_DIR, 'metadata.pkl'), 'rb') as f:
        metadata = pickle.load(f)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    yield
    # Shutdown: Cleanup resources
    del index
    del metadata
    del model

app = FastAPI(title="FAISS Search API", lifespan=lifespan)

class SearchQuery(BaseModel):
    query_text: str
    k: Optional[int] = 5

@app.post("/search")
async def search(request: SearchQuery):
    """Search for similar texts using the query text"""
    try:
        if index.ntotal == 0:
            raise HTTPException(status_code=400, detail="Index is empty")
        
        # Create embedding for the query text
        query_vector = model.encode([request.query_text])[0].astype('float32').reshape(1, -1)
        
        # Search the index
        distances, indices = index.search(query_vector, request.k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(metadata):
                result = metadata[idx].copy()
                result['distance'] = float(distances[0][i])
                results.append(result)
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/status")
async def get_status():
    """Get the current status of the index"""
    return {
        "total_vectors": index.ntotal,
        "dimension": index.d
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 