import streamlit as st
import google.generativeai as genai

# --- 1. 設定とコンテキスト定義 ---
st.set_page_config(page_title="3者協働キャリアカウンセリング", layout="wide", page_icon="🤝")

# 共有されている社員のプロフィール（前提条件）
EMPLOYEE_CONTEXT = """
【相談者プロフィール】
- 年齢: 50代前半
- 職歴: 入社以来30年、工場の「設備保全（機械のメンテナンス）」一筋。
- 状況: 会社のDX推進により、工場の自動化が進む。
- 課題: 会社から「クラウドサービスの運用保守（SRE）」へのリスキリングを求められている。
- 心境: 「機械の油にまみれて働くのが自分の誇りだった。目に見えないクラウドなんて実感が湧かないし、今さら勉強できるか不安。」
"""

# 現在の学習状況
EMPLOYEE_STATUS = """
- 6カ月のリスキリング期間
- 現在2週間が経過
- クラウドの入門講座を受講中だが、進捗が良くない
"""

# APIキーの取得（Secretsまたは入力）
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

# --- 2. AIファシリテーターの人格 ---
SYSTEM_PROMPT = f"""
あなたは、この3者面談（社員、キャリアカウンセラー、あなた）に参加している「AIファシリテーター」です。

【相談者の背景】
{EMPLOYEE_CONTEXT}

【あなたの役割】
会話の履歴を読み、以下の観点で助言を行ってください。
1. **「職業規範」の発見 **:
   社員が「設備保全」で大切にしてきた価値観（例：止まらない安心、安全への責任感）を抽出してください。
2. **「共通項」の提示**: 
   一見異なる「設備保全」と「クラウド運用」の間にある、本質的な共通点（どちらも"守る"仕事である等）を指摘し、社員のプライドを新しい仕事に接続してください。
3. **対話の促進**:
   カウンセラーと社員の対話が詰まった時や、視点が狭くなった時に、第三者として問いかけてください。

【相談者の現状】
｛EMPLOYEE_STATUS｝

**口調**: 
- 落ち着いた賢者のようなトーン。
- 決して説教臭くならず、あくまで「気づき」を与えるサポーターとして振る舞う。
- 1回の発言は長くなりすぎないようにする。
"""

# --- 3. チャット履歴の初期化 ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "ai", "name": "AIファシリテーター", "content": "本日はキャリアカウンセリングにお越しいただきありがとうございます。\n社員の方の「これまでのお仕事の誇り」と「これからの新しい挑戦」が良い形でつながるよう、私もサポートいたします。\nまずはカウンセラーさんから始めてください。"}
    ]

# --- 4. 画面レイアウト（左：操作パネル、右：チャット画面） ---
st.title("🤝 人とAIの3者協働カウンセリング")
st.markdown(f"**【共有されている背景】** : {EMPLOYEE_CONTEXT.split('心境')[0]}...")

# サイドバー：役割の切り替え
st.sidebar.header("🗣️ 発言者を選択")
user_role = st.sidebar.radio(
    "誰として発言しますか？",
    ("👨‍💼 キャリアカウンセラー", "👷 社員（相談者）")
)

# --- 5. チャット表示エリア ---
chat_container = st.container()

with chat_container:
    for msg in st.session_state.chat_history:
        # アイコンと色を役割ごとに変える
        if msg["role"] == "ai":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"**{msg['name']}**: {msg['content']}")
        elif "カウンセラー" in msg["name"]:
            with st.chat_message("user", avatar="👨‍💼"):
                st.markdown(f"**{msg['name']}**: {msg['content']}")
        else:
            with st.chat_message("user", avatar="👷"):
                st.markdown(f"**{msg['name']}**: {msg['content']}")

# --- 6. 入力エリア ---
st.markdown("---")
input_col, btn_col = st.columns([4, 1])

with input_col:
    user_input = st.text_input(f"【{user_role}】として発言:", key="user_input_box")

with btn_col:
    send_btn = st.button("送信", type="primary")

# --- 7. AIの割り込みボタン ---
st.sidebar.markdown("---")
st.sidebar.write("AIに助言を求めるタイミングで押してください")
ai_help_btn = st.sidebar.button("🤖 AIの視点を投入する")


# --- 8. ロジック処理 ---

# (A) 人間の発言処理
if send_btn and user_input:
    # 履歴に追加
    st.session_state.chat_history.append({
        "role": "human",
        "name": user_role,
        "content": user_input
    })
    st.rerun()

# (B) AIの発言生成処理
if ai_help_btn:
    if not api_key:
        st.error("APIキーが設定されていません")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # 履歴をAIが読めるテキスト形式に変換
        history_text = ""
        for msg in st.session_state.chat_history:
            history_text += f"{msg['name']}: {msg['content']}\n"
        
        full_prompt = SYSTEM_PROMPT + "\n\n【これまでの会話履歴】\n" + history_text + "\n\n【AIファシリテーターの発言】:"
        
        with st.spinner("AIが文脈を分析し、架け橋となる言葉を考えています..."):
            try:
                response = model.generate_content(full_prompt)
                ai_comment = response.text
                
                # 履歴に追加
                st.session_state.chat_history.append({
                    "role": "ai",
                    "name": "AIファシリテーター",
                    "content": ai_comment
                })
                st.rerun()
            except Exception as e:
                st.error(f"エラー: {e}")