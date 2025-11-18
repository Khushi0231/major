"""ChromaDB vector store wrapper for document embeddings"""
import os
import logging
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class ChromaStore:
    def __init__(self, collection_name: str = "documents", persist_directory: str = None):
        self.collection_name = collection_name
        self.persist_directory = persist_directory or "./chroma_db"
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "DRAVIS document embeddings"}
            )
            logger.info(f"Created new collection: {collection_name}")
    
    def add_document_chunks(
        self,
        document_id: str,
        document_name: str,
        chunks: List[tuple],
        embeddings: List[List[float]],
        upload_time: str = None
    ):
        """
        Add document chunks to the vector store.
        
        Args:
            document_id: Unique identifier for the document
            document_name: Original filename
            chunks: List of (chunk_text, metadata_dict) tuples
            embeddings: List of embedding vectors (one per chunk)
            upload_time: ISO format timestamp
        """
        if not chunks or not embeddings:
            logger.warning(f"No chunks or embeddings provided for {document_id}")
            return
        
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        
        for idx, (chunk_text, chunk_metadata) in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{idx}"
            ids.append(chunk_id)
            documents.append(chunk_text)
            
            metadata = {
                "document_id": document_id,
                "document_name": document_name,
                "chunk_index": idx,
                **chunk_metadata
            }
            if upload_time:
                metadata["upload_time"] = upload_time
            metadatas.append(metadata)
        
        # Add to collection
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(chunks)} chunks for document {document_name}")
    
    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        document_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Query the vector store for similar chunks.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            document_filter: Optional document_id to filter by
        
        Returns:
            List of result dictionaries with text, metadata, and distance
        """
        where = None
        if document_filter:
            where = {"document_id": document_filter}
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def delete_document(self, document_id: str):
        """Delete all chunks for a specific document"""
        try:
            # Get all chunks for this document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
                return len(results['ids'])
            return 0
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return 0
    
    def get_document_info(self) -> List[Dict]:
        """Get metadata about all documents in the store"""
        try:
            # Get all documents
            all_data = self.collection.get()
            
            # Group by document_id
            doc_info = {}
            for i, doc_id in enumerate(all_data['ids']):
                metadata = all_data['metadatas'][i]
                doc_id_key = metadata.get('document_id', 'unknown')
                
                if doc_id_key not in doc_info:
                    doc_info[doc_id_key] = {
                        "document_id": doc_id_key,
                        "document_name": metadata.get('document_name', 'Unknown'),
                        "upload_time": metadata.get('upload_time', ''),
                        "chunk_count": 0
                    }
                doc_info[doc_id_key]["chunk_count"] += 1
            
            return list(doc_info.values())
        except Exception as e:
            logger.error(f"Error getting document info: {e}")
            return []
    
    def get_collection_size(self) -> int:
        """Get total number of chunks in the collection"""
        try:
            return self.collection.count()
        except:
            return 0
