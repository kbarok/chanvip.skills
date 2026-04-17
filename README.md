# chanvip.skills
> Chan Master Full-Domain AI Skill | 缠中说禅 · 全域AI技能包

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)

**chanvip.skills** is a lightweight, open-source AI Skill that reproduces the core viewpoints, language style, and thinking logic of 「Chan Master」(缠中说禅). It covers **stock technical analysis, music appreciation, economic interpretation, poetry creation, and philosophical speculation** — five fields in one unified system.

Based on **RAG architecture** with **LangChain + FAISS**, it delivers accurate Q&A with authentic "Chan style" responses — no AI hallucinations, no random fabrications.

---

## 🌟 Core Features

- ✅ **Five-Domain Coverage**: Stock · Music · Economy · Poetry · Philosophy
- ✅ **RAG Architecture**: Vector retrieval from curated knowledge base — accurate, not fabricated
- ✅ **Local Deployment**: No server required, runs on Windows/Mac/Linux
- ✅ **Zero-Code Interface**: CLI (efficient) + Web UI (visual) — both beginner-friendly
- ✅ **Multi-Model Compatible**: 通义千问 · 智谱AI · ChatGLM · OpenAI · 通通支持
- ✅ **Lightweight**: ~50MB RAM, no GPU required

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (recommended 3.10)
- Any LLM API Key (通义千问 recommended for Chinese — free tier available)

### 1. Clone & Install

```bash
git clone https://github.com/chanvip/chanvip.skills.git
cd chanvip.skills

# Create virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

```bash
# Copy and edit environment file
copy .env.example .env
# Then fill in your LLM API key in .env
```

**Example `.env` for 通义千问 (recommended, free):**
```env
TONGYI_API_KEY=sk-xxxxxxxxxxxxxxxx
TONGYI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DEFAULT_MODEL=qwen-plus
```

### 3. Initialize Knowledge Base

```bash
python setup_knowledge.py
# → "Knowledge base initialized! X documents indexed."
```

### 4. Start

```bash
# CLI mode (recommended for first-time use)
python main.py --mode cli

# Web mode (visual chat, browser UI)
python main.py --mode web
# → Open http://localhost:8000 in your browser
```

---

## 💬 Usage Examples

### CLI Mode

```
==================================================
chanvip.skills — Chan Master AI
==================================================
Tip: Ask in any style — stock, poetry, philosophy, economy, or life.
Enter 'exit' to quit.

You: 禅师，什么是走势必完美？
Chan Master Style AI: 走势必完美——这是市场的根本规律。
任何级别、任何走势，终将完成。
分型、笔、线段、中枢，构成市场全部结构。
三类买卖点，是唯一安全的操作依据。
心不动，市场不动。
```

### Query Styles

**Stock (股票):**
> 缠论的核心是什么？中枢如何判断？

**Poetry (诗歌):**
> 禅师的诗有什么特点？请分析一首。

**Philosophy (哲学):**
> 如何理解"心不动，则市场不动"？

**Economy (经济):**
> 禅师怎么看当前宏观经济与A股的关系？

**Culture (文化):**
> 论语中"君子和而不同"如何理解？

---

## 📁 Knowledge Base Structure

```
knowledge/
├── cognitive/          # 认知 · 伟人思想 · 红色文化 · 实践哲学
│   ├── 01_伟人思想.txt
│   ├── 02_红色文化.txt
│   ├── 03_家国理念.txt
│   └── 04_实践哲学.txt
├── culture/            # 文化 · 论语正解
│   └── lunyu_正解.txt
├── self_cultivation/   # 修养 · 中医养生 · 诗歌修养
│   ├── 01_中医养生.txt
│   └── 02_诗歌修养.txt
└── stock/              # 股票 · 缠论核心 · 实操技巧 · 投资心性
    ├── 01_缠论核心.txt
    ├── 02_实操技巧.txt
    └── 03_投资心性.txt
```

> **Add your own materials**: Drop `.txt` files into any folder, then re-run `python setup_knowledge.py` to update the index.

---

## 🔧 Customization

### Switch LLM Provider

Edit `.env`:
```env
# 通义千问 (recommended)
DEFAULT_MODEL=tongyi

# 智谱AI
ZHIPUAI_API_KEY=your_key
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions
DEFAULT_MODEL=zhipuai

# OpenAI
OPENAI_API_KEY=sk-xxx
DEFAULT_MODEL=openai
```

### Adjust Retrieval Relevance

Edit `rag/chat.py` — change `k` parameter to control how many relevant chunks are retrieved per query.

---

## ⚠️ Disclaimer

1. **Learning & research only** — not for commercial use.
2. **Not affiliated with any individual** — this is a knowledge-base AI tool.
3. **Not investment advice** — this project does not provide stock recommendations.
4. All materials in the knowledge base are from public domain sources.
5. Users are solely responsible for how they use this project.

---

## 📄 License

MIT License — free to use, modify, distribute.

---

## 🤝 Contributing

1. Fork the repository
2. Add materials to the `knowledge/` folder
3. Re-run `python setup_knowledge.py`
4. Submit a Pull Request

---

*"诗以言志，歌以咏言。股市如道场，交易即修行。"*
