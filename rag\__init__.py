# chanvip.skills RAG Core Logic Package
# Including core functions such as knowledge base management and dialogue generation
from .knowledge_base import ChanvipKnowledgeBase
from .chat import ChanvipChat

__all__ = ["ChanvipKnowledgeBase", "ChanvipChat"]
