"""
科研助手核心类
整合文档处理、向量检索和LLM功能
"""
from typing import Dict, List, Optional
from pathlib import Path
from .document_processor import DocumentProcessor
from .vector_store import VectorStore
from .llm_agent import LLMAgent
from .web_scraper import WebScraper


class ResearchAssistant:
    """科研助手主类"""
    
    def __init__(self, documents_dir: str = "documents", 
                 use_quantization: bool = True):
        self.documents_dir = documents_dir
        self.processor = DocumentProcessor(documents_dir)
        self.vector_store = VectorStore()
        self.llm_agent = LLMAgent(use_quantization=use_quantization)
        self.web_scraper = WebScraper()
        self.documents_text = {}  # 存储完整文档文本
        self.web_contents = {}  # 存储网页内容 {title: content}
        self.is_indexed = False
    
    def initialize(self, rebuild_index: bool = False):
        """初始化助手，处理文档并构建索引"""
        index_path = Path(".cache/vector_index.faiss")
        
        if not rebuild_index and index_path.exists():
            print("加载已有索引...")
            if self.vector_store.load_index(str(index_path)):
                print("索引加载成功")
                # 需要重新加载文档文本
                self._load_documents_text()
                self.is_indexed = True
                return
        
        print("开始处理文档...")
        # 处理文档
        documents = self.processor.process_documents()
        
        if not documents:
            print("未找到可处理的文档")
            return
        
        # 保存完整文档文本
        for doc_name, chunks in documents.items():
            self.documents_text[doc_name] = "\n\n".join(chunks)
        
        # 构建向量索引
        self.vector_store.build_index(documents)
        
        # 保存索引
        self.vector_store.save_index(str(index_path))
        self.is_indexed = True
        print("初始化完成")
    
    def _load_documents_text(self):
        """从索引元数据中加载文档文本"""
        # 重新处理文档以获取完整文本
        documents = self.processor.process_documents()
        for doc_name, chunks in documents.items():
            self.documents_text[doc_name] = "\n\n".join(chunks)
    
    def ask(self, question: str, top_k: int = 5) -> str:
        """询问问题"""
        if not self.is_indexed:
            return "请先初始化助手（处理文档）。"
        
        # 检索相关文档块
        relevant_chunks = self.vector_store.search(question, top_k=top_k)
        
        if not relevant_chunks:
            return "未找到相关文档内容。"
        
        # 使用LLM生成回答
        answer = self.llm_agent.answer_question(question, relevant_chunks)
        return answer
    
    def analyze_similarity(self) -> str:
        """分析文档相似性"""
        if not self.is_indexed or len(self.documents_text) < 2:
            return "至少需要2个文档才能进行相似性分析。"
        
        return self.llm_agent.analyze_similarity(self.documents_text)
    
    def recommend_research(self) -> str:
        """推荐研究问题和方法"""
        if not self.is_indexed:
            return "请先初始化助手（处理文档）。"
        
        return self.llm_agent.recommend_research(self.documents_text)
    
    def get_document_list(self) -> List[str]:
        """获取文档列表"""
        return list(self.documents_text.keys())
    
    def fetch_web_content(self, url: str) -> Optional[Dict[str, str]]:
        """抓取网页内容"""
        result = self.web_scraper.fetch_url(url)
        if result:
            # 保存网页内容
            key = f"网页_{result['title'][:50]}" if result['title'] else f"网页_{url[:50]}"
            self.web_contents[key] = result['content']
            print(f"网页内容已保存: {key} ({result['length']} 字符)")
        return result
    
    def summarize_web_content(self, url: str, focus: str = "复习总结") -> str:
        """总结网页内容（用于复习）"""
        print(f"正在抓取并总结网页: {url}")
        web_data = self.fetch_web_content(url)
        
        if not web_data:
            return "无法抓取网页内容，请检查URL是否正确或网络连接是否正常。"
        
        # 截取内容以避免token限制
        content = web_data['content']
        if len(content) > 8000:
            content = content[:8000] + "\n\n[内容已截断...]"
        
        prompt = f"""请对以下网页内容进行{focus}，生成结构化的总结，帮助用户复习和理解：

网页标题：{web_data['title']}
网页地址：{web_data['url']}

网页内容：
{content}

请提供以下方面的总结：
1. 主要内容概述
2. 关键知识点
3. 重要概念和术语
4. 要点总结
5. 可能的实践建议或思考题

请用清晰的结构化格式输出："""
        
        return self.llm_agent.generate_response(prompt, max_length=1024)
    
    def get_web_contents_list(self) -> List[str]:
        """获取已抓取的网页内容列表"""
        return list(self.web_contents.keys())
    
    def batch_summarize_urls(self, urls: List[str], focus: str = "复习总结") -> Dict[str, str]:
        """批量总结多个网页"""
        results = {}
        for url in urls:
            print(f"\n处理URL {urls.index(url) + 1}/{len(urls)}: {url}")
            summary = self.summarize_web_content(url, focus)
            results[url] = summary
        return results

