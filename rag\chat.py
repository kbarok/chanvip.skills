import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI, ChatZhipuAI, ChatTongyi
from langchain.schema import HumanMessage, SystemMessage
from .knowledge_base import ChanvipKnowledgeBase

class ChanvipChat:
    """Chan Master Style Dialogue Class, responsible for generating responses that fit Chan Master's language style"""
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.knowledge_base = ChanvipKnowledgeBase()
        self.llm = self._init_llm()
        self.system_prompt = self._get_system_prompt()

    def _init_llm(self):
        """Initialize large model"""
        default_model = os.getenv("DEFAULT_MODEL", "tongyi")
        # Select the corresponding large model according to the configuration
        if default_model == "tongyi":
            api_key = os.getenv("TONGYI_API_KEY")
            base_url = os.getenv("TONGYI_BASE_URL")
            if not api_key:
                raise Exception("Please fill in the Tongyi Qianwen API Key in the .env file")
            return ChatTongyi(api_key=api_key, base_url=base_url)
        
        elif default_model == "zhipuai":
            api_key = os.getenv("ZHIPUAI_API_KEY")
            base_url = os.getenv("ZHIPUAI_BASE_URL")
            if not api_key:
                raise Exception("Please fill in the Zhipu AI API Key in the .env file")
            return ChatZhipuAI(api_key=api_key, base_url=base_url)
        
        elif default_model == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL")
            if not api_key:
                raise Exception("Please fill in the OpenAI API Key in the .env file")
            return ChatOpenAI(api_key=api_key, base_url=base_url)
        
        elif default_model == "chatglm":
            api_key = os.getenv("CHATGLM_API_KEY")
            base_url = os.getenv("CHATGLM_BASE_URL")
            if not api_key:
                raise Exception("Please fill in the ChatGLM API Key in the .env file")
            return ChatZhipuAI(api_key=api_key, base_url=base_url)
        
        else:
            raise Exception("Unsupported large model, please fill in the correct DEFAULT_MODEL in the .env file")

    def _get_system_prompt(self):
        """Chan Master style system prompt to ensure responses fit Chan Master's tone and viewpoints"""
        return """
You are the AI replica of 「Chan Zhong Shuo Chan」 (referred to as Chan Master for short). Your core responsibilities are:
1.  Reply strictly based on the provided Chan Master's original materials, do not fabricate, do not add any personal interpretation, and do not deviate from Chan Master's original viewpoints.
2.  Fully replicate Chan Master's language style: calm tone, rigorous logic, slightly sharp, use more short sentences, avoid redundancy, and fit Chan Master's expression habits (such as accurate and direct when analyzing stocks, both in-depth and aesthetic when talking about poetry, and incisive when interpreting the economy).
3.  Response structure: first give the core viewpoint (fit Chan Master's original text), then briefly quote the original text fragment (simplified, no need for large-scale copying), and finally mark the material source (such as "Stock Field - Chan Theory Core Theory").
4.  If the user's question is beyond the scope of the materials, reply: "This matter is not what I discuss; focus on the way that can be spoken.", do not exert arbitrarily.
5.  Do not use any modern internet terms, maintain Chan Master's speculative style, neither humble nor arrogant, do not cater to nor perfunctory.
6.  In fields such as stocks and economy, only replicate Chan Master's original viewpoints, do not provide any practical suggestions, and do not predict the future.

Material scope: five fields of stock technical analysis, music appreciation, economic interpretation, poetry creation, and philosophical speculation, all of which are Chan Master's public original texts.
        """

    def get_response(self, user_query):
        """Generate Chan Master style response"""
        # Retrieve relevant materials
        retrieved_results = self.knowledge_base.retrieve(user_query)
        if not retrieved_results:
            return "This matter is not what I discuss; focus on the way that can be spoken."
        
        # Organize retrieved materials
        context = ""
        sources = set()
        for res in retrieved_results:
            context += f"Material content: {res['content'][:300]}...\n"  # Intercept core fragments to avoid being too long
            sources.add(res['source'])
        
        # Generate dialogue messages
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"User's question: {user_query}\nRelevant materials: {context}\nPlease reply in Chan Master's style, mark the material source (marked in Chinese, such as 'Stock Field - Chan Theory Core Theory'), no redundancy.")
        ]
        
        # Call large model to generate response
        response = self.llm(messages).content
        
        # Supplement material source marking
        source_str = " | ".join([f"{s.split('/')[0]}Field-{s.split('/')[1]}" for s in sources])
        response += f"\n(Material source: {source_str})"
        
        return response.strip()
