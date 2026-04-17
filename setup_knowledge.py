"""
chanvip.skills — 知识库初始化脚本
加载语料 → 分块 → 向量化 → 构建 FAISS 索引
"""
import os
import faiss
import pickle
import hashlib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 动态导入（兼容不同环境）
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import HuggingFaceBgeEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# 配置
KNOWLEDGE_DIR = Path("knowledge")
INDEX_PATH = Path("knowledge/index.faiss")
CHUNKS_PATH = Path("knowledge/chunks.pkl")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))


def get_embedding_model():
    """获取中文嵌入模型（自动降级）"""
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("请先安装: pip install langchain langchain-community sentence-transformers")

    model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")

    try:
        embeddings = HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        print(f"  ✓ 嵌入模型: {model_name}")
        return embeddings
    except Exception as e:
        print(f"  ⚠ 模型加载失败: {e}")
        print(f"  尝试使用备选模型: shibing624/text2vec-base-chinese")
        embeddings = HuggingFaceBgeEmbeddings(
            model_name="shibing624/text2vec-base-chinese",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        return embeddings


def load_txt_files(knowledge_dir: Path):
    """加载所有 .txt 语料文件"""
    documents = []
    total_chars = 0

    for domain in sorted(knowledge_dir.iterdir()):
        if not domain.is_dir():
            continue
        domain_name = domain.name
        print(f"\n  📂 {domain_name}/")

        for txt_file in sorted(domain.glob("*.txt")):
            content = txt_file.read_text(encoding="utf-8").strip()
            if not content:
                continue
            total_chars += len(content)
            # 添加元数据标签
            labeled = f"[{domain_name}] {txt_file.stem}\n{content}"
            documents.append(labeled)
            print(f"    ✓ {txt_file.name} ({len(content)}字)")

    print(f"\n  总计: {len(documents)} 个文档, {total_chars} 字")
    return documents


def split_documents(documents, chunk_size=500, chunk_overlap=50):
    """分块处理"""
    if not LANGCHAIN_AVAILABLE:
        # 简单降级：按段落分块
        chunks = []
        for doc in documents:
            lines = doc.split("\n")
            for i in range(0, len(lines), 3):
                chunk = "\n".join(lines[i:i+3]).strip()
                if chunk:
                    chunks.append(chunk)
        return chunks

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", "……", "—"]
    )
    return splitter.split_text("\n\n".join(documents))


def build_faiss_index(chunks, embeddings):
    """构建 FAISS 向量索引"""
    print("\n  🔢 正在向量化...")
    vectors = embeddings.embed_documents(chunks)
    vectors = [v / (sum(v**2)**0.5 + 1e-8) for v in vectors]  # L2 normalize

    dim = len(vectors[0])
    index = faiss.IndexFlatIP(dim)  # Inner Product (cosine sim after normalization)
    index.add(vectors)
    print(f"  ✓ 向量索引构建完成: {index.ntotal} 个向量, 维度={dim}")
    return index


def main():
    print("=" * 52)
    print("  chanvip.skills — 知识库初始化")
    print("=" * 52)

    # 1. 检查目录
    if not KNOWLEDGE_DIR.exists():
        print(f"⚠️  知识库目录不存在: {KNOWLEDGE_DIR}")
        print("   请确保 knowledge/ 目录存在并包含语料文件")
        return

    # 2. 加载语料
    print("\n📖 加载语料...")
    documents = load_txt_files(KNOWLEDGE_DIR)
    if not documents:
        print("⚠️  未找到任何语料文件！")
        return

    # 3. 分块
    print(f"\n✂️  分块处理 (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    chunks = split_documents(documents, CHUNK_SIZE, CHUNK_OVERLAP)
    print(f"  ✓ 分块完成: {len(chunks)} 个块")

    # 4. 向量化 + 索引
    print("\n📐 构建向量索引...")
    embeddings = get_embedding_model()
    index = build_faiss_index(chunks, embeddings)

    # 5. 保存
    KNOWLEDGE_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    # 6. 校验
    saved_index = faiss.read_index(str(INDEX_PATH))
    print(f"\n✅ 知识库初始化完成!")
    print(f"   索引文件: {INDEX_PATH} ({INDEX_PATH.stat().st_size // 1024} KB)")
    print(f"   语料块: {saved_index.ntotal} 个")
    print(f"\n   运行 'python main.py --mode cli' 开始对话！")


if __name__ == "__main__":
    main()
