from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional


class BertRetriever:
    """Поиск похожих проектов с помощью BERT-эмбеддингов."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.documents: List[Dict] = []
        self.embeddings: List[torch.Tensor] = []  # <-- явно указываем тип

    def add_document(self, text: str, metadata: Optional[Dict] = None) -> None:
        """Добавить один документ в базу."""
        emb = self.model.encode(text, convert_to_tensor=True)
        self.documents.append({"text": text, "metadata": metadata or {}})
        self.embeddings.append(emb)  # <-- сохраняем тензор

    def add_folder(self, folder_path: str) -> None:
        """Загрузить все .txt-файлы из папки."""
        folder = Path(folder_path)
        if not folder.exists():
            print(f"⚠️ Папка {folder_path} не найдена")
            return
        for file_path in folder.glob("*.txt"):
            text = file_path.read_text(encoding="utf-8")
            self.add_document(text, {"source": file_path.name})

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Найти top_k похожих проектов."""
        if not self.embeddings:
            print("⚠️ Нет документов для поиска")
            return []

        # Кодируем запрос
        query_emb = self.model.encode(query, convert_to_tensor=True)
        
        # Стек эмбеддингов в один тензор
        if isinstance(self.embeddings, list):
            emb_stack = torch.stack(self.embeddings)  # <-- исправлено
        else:
            emb_stack = self.embeddings

        # Вычисляем косинусное сходство
        scores = util.cos_sim(query_emb, emb_stack)[0]
        
        # Сортируем
        top_indices = torch.argsort(scores, descending=True)[:top_k].cpu().numpy()

        results = []
        for idx in top_indices:
            results.append({
                "text": self.documents[idx]["text"],
                "metadata": self.documents[idx]["metadata"],
                "score": float(scores[idx].item())  # <-- явно извлекаем число
            })
        return results