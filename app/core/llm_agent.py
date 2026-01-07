"""
LLM Agent模块
使用量化的小模型进行问答和推理
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings("ignore")


class LLMAgent:
    """轻量级LLM Agent，支持量化加载"""
    
    def __init__(self, model_name: str = "Qwen/Qwen3-4B-Instruct-2507",
                 use_quantization: bool = True):
        """
        初始化LLM Agent
        使用Qwen2.5-0.5B小模型，适合6G显存
        """
        self.model_name = model_name
        self.use_quantization = use_quantization
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"初始化LLM Agent，设备: {self.device}")
        self._load_model()
    
    def _load_model(self):
        """加载模型（支持量化）"""
        try:
            print(f"加载模型: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )

            if self.use_quantization and self.device == "cuda":
                # 使用4-bit量化以节省显存
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    quantization_config=quantization_config,
                    device_map="auto",
                    trust_remote_code=True,
                    dtype=torch.float16
                )
            else:
                # CPU模式或非量化模式
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
                if self.device == "cuda":
                    self.model = self.model.to(self.device)

            print("模型加载完成")
        except Exception as e:
            print(f"模型加载失败: {e}")
            print("尝试使用更小的模型或CPU模式...")
            # 如果加载失败，使用更小的模型
            self.model_name = "microsoft/DialoGPT-small"
            self._load_fallback_model()

    def _load_fallback_model(self):
        """加载备用模型"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            if self.device == "cuda":
                self.model = self.model.to(self.device)
        except Exception as e:
            print(f"备用模型加载也失败: {e}")
            self.model = None
    
    def generate_response(self, prompt: str, max_length: int = 512, 
                         temperature: float = 0.7) -> str:
        """生成回答"""
        if self.model is None or self.tokenizer is None:
            return "模型未正确加载，请检查配置。"
        
        try:
            # 构建输入
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # 格式化输入（根据模型类型）
            if "Qwen" in self.model_name:
                text = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            else:
                text = prompt
            
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
            
            # 生成
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 解码
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )
            
            return response.strip()
        except Exception as e:
            return f"生成回答时出错: {e}"
    
    def answer_question(self, question: str, context_chunks: List[Dict]) -> str:
        """基于上下文回答问题"""
        if not context_chunks:
            return "未找到相关文档内容。"
        
        # 构建上下文
        context = "\n\n".join([
            f"[文档: {chunk['doc_name']}]\n{chunk['chunk']}"
            for chunk in context_chunks[:3]  # 只使用前3个最相关的块
        ])
        
        prompt = f"""基于以下文档内容回答问题。如果文档中没有相关信息，请说明。

文档内容：
{context}

问题：{question}

回答："""
        
        return self.generate_response(prompt, max_length=256)
    
    def analyze_similarity(self, documents: Dict[str, str]) -> str:
        """分析多个文档的相似性"""
        if len(documents) < 2:
            return "至少需要2个文档才能进行相似性分析。"
        
        doc_names = list(documents.keys())
        doc_texts = list(documents.values())
        
        # 构建分析提示
        context = "\n\n".join([
            f"文档{i+1}: {name}\n内容摘要: {text[:500]}..."
            for i, (name, text) in enumerate(zip(doc_names, doc_texts))
        ])
        
        prompt = f"""请分析以下多个科研文档的相似性，重点关注：
1. 研究问题的相似性
2. 研究方法的相似性
3. 研究思路的相似性
4. 可能的交叉点和互补性

文档内容：
{context}

请提供详细的分析："""
        
        return self.generate_response(prompt, max_length=512)
    
    def recommend_research(self, documents: Dict[str, str]) -> str:
        """推荐研究问题和方法"""
        context = "\n\n".join([
            f"文档: {name}\n内容摘要: {text[:500]}..."
            for name, text in documents.items()
        ])
        
        prompt = f"""基于以下科研文档，请推荐：
1. 值得进一步研究的问题
2. 可能的研究方法或技术路线
3. 潜在的研究方向

文档内容：
{context}

请提供详细的推荐："""
        
        return self.generate_response(prompt, max_length=512)

