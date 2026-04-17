"""
chanvip.skills — Web 界面
简洁禅意风格聊天界面
"""
import os
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# 动态导入（避免主程序依赖 web）
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from rag.chat import ChanvipChat

# 全局聊天实例
_chat_instance = None


def get_chat():
    global _chat_instance
    if _chat_instance is None:
        _chat_instance = ChanvipChat()
    return _chat_instance


# Flask 应用
app = Flask(__name__, template_folder="templates")
app.config["JSON_AS_ASCII"] = False


# --- HTML 模板 ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>chanvip.skills — 缠中说禅</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
    min-height:100vh; display:flex; align-items:center; justify-content:center;
  }
  .container {
    width: min(720px, 95vw);
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 32px 28px;
    box-shadow: 0 24px 64px rgba(0,0,0,0.4);
  }
  h1 {
    text-align:center; color:#c8a97e; font-size:1.6rem;
    margin-bottom:6px; letter-spacing:4px;
  }
  .subtitle {
    text-align:center; color:#666; font-size:0.85rem;
    margin-bottom:28px; letter-spacing:2px;
  }
  .chat-box {
    background: rgba(0,0,0,0.25); border-radius:10px;
    padding: 20px; min-height:280px; max-height:420px;
    overflow-y:auto; margin-bottom:16px;
    border:1px solid rgba(255,255,255,0.05);
  }
  .msg { margin-bottom:16px; line-height:1.7; }
  .msg.user { color:#a0c4ff; font-size:0.95rem; }
  .msg.chan { color:#e8d5b0; font-size:0.95rem; white-space:pre-wrap; }
  .msg.chan::before { content:'禅: '; color:#c8a97e; }
  .msg.system { color:#666; font-size:0.82rem; text-align:center; font-style:italic; }
  .input-row { display:flex; gap:10px; }
  input {
    flex:1; background: rgba(255,255,255,0.06);
    border:1px solid rgba(255,255,255,0.12); border-radius:8px;
    padding:12px 16px; color:#e0e0e0; font-size:0.95rem; outline:none;
  }
  input:focus { border-color:#c8a97e; }
  button {
    background:#c8a97e; color:#0a0a0a; border:none;
    border-radius:8px; padding:12px 24px;
    font-size:0.95rem; cursor:pointer; font-weight:bold;
    transition: opacity 0.2s;
  }
  button:hover { opacity:0.85; }
  button:disabled { opacity:0.4; cursor:not-allowed; }
  .hint {
    text-align:center; color:#555; font-size:0.78rem;
    margin-top:14px; line-height:1.6;
  }
  ::-webkit-scrollbar { width:4px; }
  ::-webkit-scrollbar-thumb { background:#c8a97e; border-radius:2px; }
</style>
</head>
<body>
<div class="container">
  <h1>CHANVIP</h1>
  <div class="subtitle">缠中说禅 · 全域AI技能包</div>
  <div class="chat-box" id="chatBox">
    <div class="msg system">缠中说禅 — 心不动，市场不动。输入问题，开启修行。</div>
  </div>
  <div class="input-row">
    <input id="msgInput" placeholder="输入问题... (股票/诗歌/哲学/经济/文化)" autocomplete="off" />
    <button id="sendBtn" onclick="sendMsg()">发送</button>
  </div>
  <div class="hint">
    💡 示例: 「什么是走势必完美？」 「禅师如何看当前经济？」 「分析一首诗」<br>
    <a href="https://github.com/chanvip/chanvip.skills" style="color:#666;">View on GitHub →</a>
  </div>
</div>
<script>
  const chatBox = document.getElementById('chatBox');
  const input = document.getElementById('msgInput');
  const sendBtn = document.getElementById('sendBtn');

  function scrollBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function sendMsg() {
    const q = input.value.trim();
    if (!q) return;
    appendMsg('user', q);
    input.value = '';
    sendBtn.disabled = true;
    appendMsg('system', '正在思考...');

    fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: q})
    })
    .then(r => r.json())
    .then(d => {
      // 移除 "正在思考"
      chatBox.querySelectorAll('.msg.system').forEach(el => el.remove());
      appendMsg('chan', d.answer || d.error || '暂无回应');
      sendBtn.disabled = false;
    })
    .catch(e => {
      chatBox.querySelectorAll('.msg.system').forEach(el => el.remove());
      appendMsg('chan', '⚠️ 连接失败，请检查服务是否启动');
      sendBtn.disabled = false;
    });
  }

  function appendMsg(cls, text) {
    const div = document.createElement('div');
    div.className = 'msg ' + cls;
    div.textContent = text;
    chatBox.appendChild(div);
    scrollBottom();
  }

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') sendMsg();
  });
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "问题不能为空"})

    try:
        chat = get_chat()
        answer = chat.get_response(question)
        return jsonify({"answer": answer})
    except FileNotFoundError as e:
        return jsonify({"error": f"⚠️ {e}\n请先运行: python setup_knowledge.py"})
    except Exception as e:
        return jsonify({"error": f"⚠️ 运行时错误: {e}"})


def run_web_app(chat_instance=None):
    global _chat_instance
    if chat_instance:
        _chat_instance = chat_instance

    host = os.getenv("WEB_HOST", "0.0.0.0")
    port = int(os.getenv("WEB_PORT", "8000"))
    debug = os.getenv("WEB_DEBUG", "false").lower() == "true"

    # 预热聊天引擎
    try:
        get_chat()
        print(f"  ✓ 聊天引擎初始化成功")
    except Exception as e:
        print(f"  ⚠️ 聊天引擎初始化: {e}")

    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    run_web_app()
