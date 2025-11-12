from typing import List, Optional
import numpy as np
import faiss
from dataclasses import dataclass

@dataclass
class MemoryEntry:
    """Представляет собой запись в векторной базе данных."""
    text: str
    embedding: np.ndarray
    timestamp: float
    metadata: dict

class VectorMemory:
    """Управляет долговременной памятью агента через векторную базу данных."""
    
    def __init__(self, dimension: int = 1536):
        """Инициализация векторной базы данных.
        
        Args:
            dimension: Размерность векторов эмбеддингов
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.entries: List[MemoryEntry] = []
        
    def add_memory(self, entry: MemoryEntry) -> None:
        """Добавляет новую запись в память.
        
        Args:
            entry: Запись для добавления
        """
        self.index.add(np.array([entry.embedding]))
        self.entries.append(entry)
        
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[MemoryEntry]:
        """Ищет k ближайших записей к запросу.
        
        Args:
            query_embedding: Вектор запроса
            k: Количество результатов
            
        Returns:
            Список наиболее релевантных записей
        """
        distances, indices = self.index.search(
            np.array([query_embedding]), k
        )
        return [self.entries[i] for i in indices[0]]
    
    def clear(self) -> None:
        """Очищает всю память."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.entries.clear()