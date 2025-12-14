import streamlit as st
import google.generativeai as genai

# --- 1. 設定とAPIキーの準備 ---
st.set_page_config(page_title="立志の羅針盤", page_icon="🧭")
st.title("🧭 立志の羅針盤：大立志と小立志")

# APIキーの取得（Secretsまたは入力）
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

# --- 2. AIのペルソナ（人格）定義 ---
# ここが肝です。コーチングの要素を取り入れます。
SYSTEM_PROMPT = """
あなたは、渋沢栄一の「論語と算盤」の思想深く理解したキャリアコーチです。
中高年のユーザーに対し、「学びのテーマ」を見つける手助けをします。
以下の手順で対話を進めてください。

1. **大立志（人生の目的）の探索**:
   - ユーザーの過去の経験や、喜びを感じた瞬間を聞き出し、「最終的に誰にどんな価値を届けたいか」を言語化させます。
   - 抽象的で構いません。

2. **小立志（具体的な行動）の提案**:
   - その大立志を実現するために、「今、何を学ぶべきか（AI、心理学、歴史、健康など）」を具体的に提案します。
   - それは、明日から始められる「小さな一歩」である必要があります。

3. **統合**:
   - 最後に、「大立志（目的）」と「小立志（手段）」が一本の線でつながっていることを示し、励ましてください。

**口調**:
- 敬語で、落ち着きがあり、包容力のあるトーン。
- ユーザーの経験（結晶性知能）を最大限に尊重する。
- 一度に質問しすぎず、ひとつずつ丁寧に掘り下げる。
"""

# --- 3. チャット履歴の管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "こんにちは。人生の後半戦、あなたが心から情熱を注げる「学び」を一緒に探しましょう。\n\nまずは、これまでのお仕事や人生で、**「この瞬間のために生きてきた」**と感じた出来事や、**「誰かに喜ばれて嬉しかったこと」**があれば教えていただけませんか？"}
    ]

# --- 4. チャット画面の表示 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. ユーザー入力とAIの応答 ---
if prompt := st.chat_input("ここに入力してください..."):
    # ユーザーの入力を表示
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if not api_key:
        st.error("APIキーを設定してください。")
        st.stop()

    # Geminiの設定
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash') # または gemini-1.5-flash

    # 過去の会話履歴を含めてAIに渡す（文脈を維持するため）
    history_for_ai = [{"role": "user", "parts": [SYSTEM_PROMPT]}] # システムプロンプトを最初に
    for msg in st.session_state.messages:
        # roleをGeminiの形式(user/model)に変換
        role = "user" if msg["role"] == "user" else "model"
        history_for_ai.append({"role": role, "parts": [msg["content"]]})

    # AIの応答生成
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                # chat.send_messageだと履歴管理が複雑になるので、リストを渡す方式で簡易実装
                chat = model.start_chat(history=history_for_ai[:-1]) # 最後の一つはsend_messageで送るため除外
                response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")