import os
import faiss
import numpy as np
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

def load_knowledge_files(knowledge_dir):
    """Load all TXT file contents in the knowledge base"""
    knowledge_text = []
    # Traverse all field folders
    for domain in os.listdir(knowledge_dir):
        domain_path = os.path.join(knowledge_dir, domain)
        if not os.path.isdir(domain_path):
            continue
        # Traverse all TXT files under the field
        for file in os.listdir(domain_path):
            if file.endswith(".txt"):
                file_path = os.path.join(domain_path, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            # Mark material source (field + file name)
                            source = f"{domain}/{file[:-4]}"
                            knowledge_text.append((content, source))
                except Exception as e:
                    print(f"Failed to load file {file_path}: {str(e)}")
    return knowledge_text

def split_text(knowledge_text, chunk_size, chunk_overlap):
    """Chunk materials to improve retrieval accuracy"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "，", "；", "！", "？"]
    )
    chunks = []
    sources = []
    for text, source in knowledge_text:
        splits = text_splitter.split_text(text)
        chunks.extend(splits)
        sources.extend([source] * len(splits))
    return chunks, sources

def build_faiss_index(embeddings, chunks):
    """Build FAISS vector index"""
    # Generate vectors
    vectors = embeddings.embed_documents(chunks)
    vectors = np.array(vectors).astype("float32")
    
    # Build index
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)
    
    return index

def save_index_and_sources(index, sources, index_path, sources_path):
    """Save vector index and material sources"""
    # Save FAISS index
    faiss.write_index(index, index_path)
    # Save material sources (corresponding to the index)
    with open(sources_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sources))
    print(f"Index saved to: {index_path}")
    print(f"Material sources saved to: {sources_path}")

def main():
    print("="*50)
    print("chanvip.skills Knowledge Base Initialization")
    print("="*50)
    
    # Read configuration
    knowledge_dir = os.getenv("KNOWLEDGE_DIR", "./knowledge")
    chunk_size = int(os.getenv("CHUNK_SIZE", 500))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 50))
    index_path = os.getenv("FAISS_INDEX_PATH", "./knowledge/index.faiss")
    sources_path = os.path.join(os.path.dirname(index_path), "sources.txt")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text2vec-base-chinese")
    
    # Check knowledge base directory
    if not os.path.exists(knowledge_dir):
        os.makedirs(knowledge_dir)
        print(f"Knowledge base directory does not exist, automatically created: {knowledge_dir}")
        print("Please add Chan Master related materials (TXT format) in the knowledge/ directory first, then run this script again")
        return
    
    # Load materials
    print(f"Loading knowledge base materials (directory: {knowledge_dir})...")
    knowledge_text = load_knowledge_files(knowledge_dir)
    if not knowledge_text:
        print("No valid materials found, please add Chan Master related TXT materials in the knowledge/ directory")
        return
    print(f"Successfully loaded {len(knowledge_text)} material files")
    
    # Material chunking
    print(f"Chunking materials (chunk size: {chunk_size}, overlap: {chunk_overlap})...")
    chunks, sources = split_text(knowledge_text, chunk_size, chunk_overlap)
    print(f"Material chunking completed, total {len(chunks)} chunks")
    
    # Initialize embedding model
    print(f"Initializing embedding model ({embedding_model})...")
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    
    # Build FAISS vector index
    print("Building FAISS vector index...")
    index = build_faiss_index(embeddings, chunks)
    print("Vector index built successfully")
    
    # Save index and sources
    save_index_and_sources(index, sources, index_path, sources_path)
    
    print("="*50)
    print("Knowledge base initialization completed! You can start main.py to use it")
    print("="*50)

if __name__ == "__main__":
    main()
