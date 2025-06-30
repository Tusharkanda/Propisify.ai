import chromadb
import pandas as pd
import uuid
import logging
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import Union
import os
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


class DataManager:
    def __init__(self, persist_directory: str = "./chromadb_data"):
        """
        Initialize DataManager with persistent ChromaDB client and logger.
        """
        self.logger = logging.getLogger(__name__)
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None

    def initialize_database(self):
        """
        Set up ChromaDB client and collection for proposals.
        """
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)            
            
            # Use ChromaDB's default embedding function for compatibility
            embedding_fn = embedding_functions.DefaultEmbeddingFunction()

            self.collection = self.client.get_or_create_collection(
                name="proposals",
                embedding_function=embedding_fn #type: ignore
            )
            
            self.logger.info("ChromaDB collection 'proposals' initialized.")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {str(e)}")
            raise Exception(f"Database initialization error: {str(e)}")

    def store_proposal(self, text: str, metadata: dict) -> bool:
        """
        Store a proposal's text and metadata in ChromaDB with a unique ID.
        Args:
            text (str): Proposal text
            metadata (dict): Dict with keys 'client_name', 'industry', 'service_type'
        Returns:
            bool: Success status
        """
        try:
            if not self.collection:
                raise Exception("ChromaDB collection not initialized.")
            proposal_id = str(uuid.uuid4())
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[proposal_id]
            )
            # Persist to disk after adding

            # if self.client:
            #     self.client.persist()

            return True
        except Exception as e:
            self.logger.error(f"Failed to store proposal: {str(e)}")
            return False

    def search_similar_proposals(self, query: str, industry: Union[str, None] = None, service_type: Union[str, None] = None):
        """
        Search for similar proposals using vector similarity and optional filters.
        Args:
            query (str): Search query
            industry (str, optional): Industry filter
            service_type (str, optional): Service type filter
        Returns:
            list: Top 3 most similar proposals with text and metadata
        """
        try:
            if not self.collection:
                raise Exception("ChromaDB collection not initialized.")
            
            where = None
            if industry and service_type:
                where = {
                    "$and": [
                        {"industry": industry},
                        {"service_type": service_type}
                    ]
                }
            elif industry:
                where = {"industry": industry}
            elif service_type:
                where = {"service_type": service_type}

            query_args = {
                "query_texts": [query],
                "n_results": 5
            }
            if where:
                query_args["where"] = where

            results = self.collection.query(**query_args)


            docs = []
            documents_list = results.get("documents", [[]])
            metadatas_list = results.get("metadatas", [[]])

            if documents_list is None or len(documents_list) == 0:
                return []
            if metadatas_list is None or len(metadatas_list) == 0:
                metadatas_list = [[]]

            documents = documents_list[0]
            metadatas = metadatas_list[0]

            for i in range(len(documents)):
                doc = {
                    "text": documents[i],
                    "metadata": metadatas[i] if i < len(metadatas) else {}
                }
                docs.append(doc)
            return docs
        
        except Exception as e:
            self.logger.error(f"Failed to search proposals: {str(e)}")
            return []

    def get_all_proposals(self):
        """
        Return all stored proposals with their metadata for UI display.
        Returns:
            list: All proposals with text and metadata
        """
        try:
            if not self.collection:
                raise Exception("ChromaDB collection not initialized.")
            results = self.collection.get()
            docs = []
            documents = results.get("documents")
            metadatas = results.get("metadatas")
            if documents is None or metadatas is None:
                return []
            for i in range(len(documents)):
                doc = {
                    "text": documents[i],
                    "metadata": metadatas[i]
                }
                docs.append(doc)
            return docs
        except Exception as e:
            self.logger.error(f"Failed to retrieve all proposals: {str(e)}")
            return []
        