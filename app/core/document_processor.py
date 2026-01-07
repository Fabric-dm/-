"""
PDF文档处理模块
负责PDF文档的读取、文本提取和分块
"""
import os
import pdfplumber
from typing import List, Dict
from pathlib import Path


class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self, documents_dir: str = "documents"):
        self.documents_dir = Path(documents_dir)
        self.documents_dir.mkdir(exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """从PDF中提取文本"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"提取PDF文本时出错 {pdf_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """将文本分块，用于向量化"""
        if not text:
            return []
        
        # 按段落分割
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            # 如果当前块加上新段落不超过chunk_size，则添加
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                # 保存当前块
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # 如果段落本身很长，需要进一步分割
                if len(para) > chunk_size:
                    words = para.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 <= chunk_size:
                            temp_chunk += word + " "
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            temp_chunk = word + " "
                    current_chunk = temp_chunk
                else:
                    current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def process_documents(self) -> Dict[str, List[str]]:
        """处理所有PDF文档"""
        documents = {}
        pdf_files = list(self.documents_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"在 {self.documents_dir} 中未找到PDF文件")
            return documents
        
        print(f"找到 {len(pdf_files)} 个PDF文件，开始处理...")
        
        for pdf_path in pdf_files:
            print(f"处理: {pdf_path.name}")
            text = self.extract_text_from_pdf(str(pdf_path))
            if text:
                chunks = self.chunk_text(text)
                documents[pdf_path.name] = chunks
                print(f"  - 提取了 {len(chunks)} 个文本块")
        
        return documents

