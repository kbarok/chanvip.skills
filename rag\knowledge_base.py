import os
import faiss
import numpy as np
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings

class ChanvipKnowledgeBase:
    """Chan Master Full-Domain Knowledge Base Management Class, responsible for material retrieval and index loading"""
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self._init_config()
        self._init_embeddings()
        self._load_index_and_sources()

    def _init_config(self):
        """Initialize configuration"""
        self.knowledge_dir = os.getenv("KNOWLEDGE_DIR", "./knowledge")
        self.index_path = os.getenv("FAISS_INDEX_PATH", "./knowledge/index.faiss")
        self.sources_path = os.path.join(os.path.dirname(self.index_path), "sources.txt")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text2vec-base-chinese")
        self.top_k = 3  # Retrieve Top K relevant materials

    def _init_embeddings(self):
        """Initialize embedding model"""
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)

    def _load_index_and_sources(self):
        """Load FAISS vector index and material sources"""
        if not os.path.exists(self.index_path) or not os.path.exists(self.sources_path):
            raise Exception("Knowledge base index not found, please run setup_knowledge.py to initialize the knowledge base first")
        
        # Load FAISS index
        self.index = faiss.read_index(self.index_path)
        # Load material sources
        with open(self.sources_path, "r", encoding="utf-8") as f:
            self.sources = f.read().split("\n")

    def retrieve(self, query):
        """Retrieve materials related to the query"""
        # Generate query vector
        query_vector = self.embeddings.embed_query(query)
        query_vector = np.array([query_vector]).astype("float32")
        
        # Retrieve Top K relevant materials
        distances, indices = self.index.search(query_vector, self.top_k)
        
        # Organize retrieval results (deduplication, sorting by relevance)
        results = []
        seen = set()
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.sources):
                continue
            source = self.sources[idx]
            if source in seen:
                continue
            seen.add(source)
            # Read material content (read from the corresponding TXT file)
            domain, filename = source.split("/")
            file_path = os.path.join(self.knowledge_dir, domain, f"{filename}.txt")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    results.append({
                        "content": content,
                        "source": source,
                        "distance": distances[0][i]
                    })
        
        # Sort by distance (smaller distance means higher relevance)
        results.sort(key=lambda x: x["distance"])
        return results

    def add_knowledge(self, content, domain, filename):
        """Add new knowledge base materials (take effect after re-running setup_knowledge.py)"""
        domain_path = os.path.join(self.knowledge_dir, domain)
        if not os.path.exists(domain_path):
            os.makedirs(domain_path)
        file_path = os.path.join(domain_path, f"{filename}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"Material has been added to: {file_path}, please run setup_knowledge.py to re-initialize the knowledge base")
