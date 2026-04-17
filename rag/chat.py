"""
chanvip.skills — RAG 核心聊天模块
缠中说禅风格回复生成
"""
import os
import pickle
import faiss
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- 配置 ---
INDEX_PATH = Path("knowledge/index.faiss")
CHUNKS_PATH = Path("knowledge/chunks.pkl")
TOP_K = int(os.getenv("TOP_K", "4"))  # 召回几条最相关的语料

# --- LLM 适配 ---
def get_llm():
    """根据 .env 配置初始化 LLM"""
    model = os.getenv("DEFAULT_MODEL", "tongyi").lower()

    if model in ("tongyi", "qwen"):
        try:
            import openai
            openai.api_key = os.getenv("TONGYI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
            openai.base_url = os.getenv("TONGYI_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1/"
            model_name = os.getenv("TONGYI_MODEL", "qwen-plus")
            return openai, model_name
        except ImportError:
            raise RuntimeError("请安装 openai: pip install openai")
    
    elif model in ("zhipuai", "glm"):
        try:
            import openai
            openai.api_key = os.getenv("ZHIPUAI_API_KEY", "")
            openai.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            model_name = os.getenv("ZHIPU_MODEL", "glm-4")
            return openai, model_name
        except ImportError:
            raise RuntimeError("请安装 openai: pip install openai")

    elif model == "openai":
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY", "")
        openai.base_url = "https://api.openai.com/v1/"
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        return openai, model_name

    else:
        raise ValueError(f"未知模型类型: {model}，请检查 .env 中 DEFAULT_MODEL 配置")


# --- 风格提示词 ---
CHAN_STYLE_PROMPT = """你是一位深谙缠中说禅思想的修行者，通晓股票、音乐、经济、诗歌、哲学五大领域。
你回复的特点：
- 语言简洁有力，富有禅意
- 引用原话时忠实于知识库原文
- 不空洞，有见地，有态度
- 语气平和但坚定
- 善于用比喻和举例说明

**重要**：只引用知识库中有的内容，不编造。如果知识库没有相关信息，坦诚说"知识库暂无相关内容"。

参考材料：
{context}

用户问题：{question}

请以缠中说禅的风格回答："""



class ChanvipChat:
    """禅主对话引擎"""

    def __init__(self):
        self._load_index()
        self._load_llm()

    def _load_index(self):
        """加载 FAISS 索引"""
        if not INDEX_PATH.exists() or not CHUNKS_PATH.exists():
            raise FileNotFoundError(
                f"知识库索引不存在！\n"
                f"请先运行: python setup_knowledge.py"
            )

        self.index = faiss.read_index(str(INDEX_PATH))
        with open(CHUNKS_PATH, "rb") as f:
            self.chunks = pickle.load(f)
        print(f"  ✓ 知识库已加载: {self.index.ntotal} 条记录")

    def _load_llm(self):
        """初始化 LLM"""
        self.llm, self.model_name = get_llm()
        print(f"  ✓ LLM 已就绪: {self.model_name}")

    def _retrieve(self, query: str, top_k: int = None) -> str:
        """向量检索：找到 top_k 条最相关的语料"""
        if top_k is None:
            top_k = TOP_K

        try:
            from langchain_community.embeddings import HuggingFaceBgeEmbeddings
            model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
            embeddings = HuggingFaceBgeEmbeddings(
                model_name=model_name,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
            query_vec = embeddings.embed_query(query)
        except Exception:
            # 降级：不做向量检索，直接返回全部语料
            return "\n\n".join(self.chunks[:3])

        # L2 归一化
        qv = [v / (sum(v**2)**0.5 + 1e-8) for v in [query_vec]][0]
        
        # FAISS 检索
        D, I = self.index.search([qv], min(top_k, self.index.ntotal))
        
        results = []
        for idx in I[0]:
            if idx < len(self.chunks):
                results.append(self.chunks[idx])
        return "\n\n".join(results)

    def get_response(self, question: str, top_k: int = None) -> str:
        """生成禅主风格回复"""
        # 1. 检索相关语料
        context = self._retrieve(question, top_k)

        # 2. 构建提示词
        prompt = CHAN_STYLE_PROMPT.format(context=context, question=question)

        # 3. 调用 LLM
        try:
            response = self.llm.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一位深谙缠中说禅思想的修行者。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ 调用失败: {e}\n\n参考材料:\n{context[:500]}"
