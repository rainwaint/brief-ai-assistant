import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Dict, Optional

class ProjectRetriever:
    def __init__(self, collection_name: str = "projects", persist_dir: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def add_project(self, project_text: str, metadata: Optional[Dict] = None) -> None:
        embedding = self.encoder.encode(project_text).tolist()
        doc_id = str(hash(project_text))
        self.collection.add(
            documents=[project_text],
            embeddings=[embedding],
            metadatas=[metadata or {}],
            ids=[doc_id]
        )
        print(f"✅ Добавлен проект: {metadata.get('source', 'без имени')}")

    def add_projects_from_folder(self, folder_path: str) -> None:
        folder = Path(folder_path)
        if not folder.exists():
            print(f"⚠️ Папка {folder_path} не найдена")
            return
        for file_path in folder.glob("*.txt"):
            text = file_path.read_text(encoding="utf-8")
            self.add_project(text, {"source": file_path.name})

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        query_embedding = self.encoder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        retrieved = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                retrieved.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                })
        return retrieved