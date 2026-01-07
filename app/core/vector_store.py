"""
向量存储模块
使用sentence-transformers和FAISS实现文档向量化和检索
"""
import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
from pathlib import Path


class VectorStore:
    """向量存储和检索"""
    
    def __init__(self, model_name: str = "BAAI/bge-large-zh-v1.5",
                 cache_dir: str = ".cache"):
        """
        初始化向量存储
        使用轻量级的多语言模型，适合6G显存
        """
        self.model_name = model_name
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        print(f"加载embedding模型: {model_name}")
        # 使用CPU模式以节省显存
        self.embedding_model = SentenceTransformer(model_name, device='cpu')
        self.index = None
        self.documents = []
        self.metadata = []  # 存储文档来源信息
        
    def build_index(self, documents: Dict[str, List[str]]):
        """构建向量索引"""
        print("构建向量索引...")
        
        all_chunks = []
        self.metadata = []
        
        for doc_name, chunks in documents.items():
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                self.metadata.append({
                    'doc_name': doc_name,
                    'chunk_id': i,
                    'chunk': chunk
                })
        
        if not all_chunks:
            print("没有文档内容可索引")
            return
        
        print(f"正在向量化 {len(all_chunks)} 个文本块...")
        # 批量向量化
        embeddings = self.embedding_model.encode(
            all_chunks,
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True
        )
        
        # 创建FAISS索引
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        self.documents = all_chunks
        
        print(f"索引构建完成，共 {self.index.ntotal} 个向量")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相关文档块"""
        if self.index is None or len(self.documents) == 0:
            return []
        
        # 向量化查询
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True
        ).astype('float32')
        
        # 搜索
        distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                results.append({
                    'doc_name': self.metadata[idx]['doc_name'],
                    'chunk_id': self.metadata[idx]['chunk_id'],
                    'chunk': self.metadata[idx]['chunk'],
                    'distance': float(distances[0][i])
                })
        
        return results
    
    def get_document_embedding(self, text: str) -> np.ndarray:
        """获取文档的整体向量表示"""
        embedding = self.embedding_model.encode(
            [text],
            convert_to_numpy=True
        )
        return embedding[0]
    
    def save_index(self, path: str):
        """保存索引"""
        save_path = Path(path)
        save_path.parent.mkdir(exist_ok=True)
        
        faiss.write_index(self.index, str(save_path))
        
        # 保存元数据
        metadata_path = save_path.parent / f"{save_path.stem}_metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)
    
    def load_index(self, path: str):
        """加载索引"""
        load_path = Path(path)
        
        if not load_path.exists():
            return False
        
        self.index = faiss.read_index(str(load_path))
        
        # 加载元数据
        metadata_path = load_path.parent / f"{load_path.stem}_metadata.pkl"
        if metadata_path.exists():
            with open(metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadata = data['metadata']
        
        return True

