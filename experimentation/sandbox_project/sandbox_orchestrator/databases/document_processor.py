from typing import Dict, List, Optional, Union
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with a sentence transformer model."""
        self.model = SentenceTransformer(model_name)
        logger.info(f"Initialized document processor with model: {model_name}")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for a text string."""
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def process_documents(
        self,
        documents_file: Path
    ) -> Dict[str, List[Dict]]:
        """Process documents from a JSON file and add embeddings."""
        try:
            # Load documents
            with open(documents_file) as f:
                data = json.load(f)
            
            processed_collections = {}
            
            # Process each collection
            for collection_name, collection_data in data.get("collections", {}).items():
                processed_points = []
                
                for point in collection_data.get("points", []):
                    # Get text to embed
                    text = point["payload"].get("text", "")
                    if not text:
                        logger.warning(f"No text found in point: {point}")
                        continue
                    
                    # Generate embedding
                    embedding = self.embed_text(text)
                    
                    # Create processed point
                    processed_point = {
                        "id": point["id"],
                        "vector": embedding,
                        "payload": point["payload"]
                    }
                    processed_points.append(processed_point)
                
                processed_collections[collection_name] = {
                    "vector_size": len(processed_points[0]["vector"]) if processed_points else 768,
                    "distance": collection_data.get("distance", "cosine"),
                    "points": processed_points
                }
            
            return processed_collections
            
        except Exception as e:
            logger.error(f"Error processing documents: {e}")
            raise
    
    def save_processed_documents(
        self,
        processed_data: Dict[str, List[Dict]],
        output_file: Path
    ) -> None:
        """Save processed documents with embeddings."""
        try:
            with open(output_file, 'w') as f:
                json.dump(processed_data, f, indent=2)
            logger.info(f"Saved processed documents to {output_file}")
        except Exception as e:
            logger.error(f"Error saving processed documents: {e}")
            raise