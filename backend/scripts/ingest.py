"""Ingest real agricultural PDFs from backend/knowledge into the vector store.
Usage (from backend/):  python -m scripts.ingest"""
import json
from app.services import rag_service

print(json.dumps(rag_service.ingest_directory(), indent=2))
