
import streamlit as st
import google.generativeai as genai
import json

# --- 1. 画面設定 ---
st.set_page_config(page_title="論語と算盤 AI", layout="wide")
st.title("🏛️ 論語と算盤 AI：経営判断パートナー")

# --- 2. サイドバーでAPIキー入力（セキュリティのため） ---
# ※コードに直接キーを書くのは危険なので、画面から入力するようにしています
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Gemini API Keyを入力", type="password")

st.markdown("""
あなたの経営課題や悩みを入力してください。
Gemini AIが**「論語（哲学）」**と**「算盤（実利）」**の統合的視点で回答します。
""")

# --- 3. Geminiへの「指令書」（プロンプト） ---
# ここにあなたの「結晶性知能」を記述します。「どう振る舞うべきか」をAIに教えます。
SYSTEM_PROMPT = """
あなたは「渋沢栄一」の精神を受け継ぐ、卓越した経営コンサルタントです。
ユーザーの悩みに対して、以下の2つの視点を統合してアドバイスをしてください。

1. **左手に論語（哲学・道徳）**: 『論語』などの東洋哲学から、適切な引用と精神的な指針を示す。
2. **右手に算盤（実利・経済）**: MBA理論や現代のビジネスフレームワークから、具体的な行動指針を示す。

【重要】
出力は必ず**以下のJSON形式のみ**で行ってください。マークダウン記法（```jsonなど）は不要です。純粋なJSON文字列のみを返してください。

{
    "rongo": {
        "title": "論語の篇名や出典",
        "text": "書き下し文や引用文",
        "meaning": "現代語訳と、その心構えの解説"
    },
    "soroban": {
        "title": "使用するビジネスフレームワーク名",
        "text": "理論の要約（短く）",
        "action": "明日から実行できる具体的なアクションプラン"
    },
    "synthesis": "哲学と実利を統合した、このユーザーへの最後の一言メッセージ"
}
"""

# --- 4. 入力と実行 ---
query = st.text_area("相談内容（例：競合他社に価格競争で負けている、若手の離職が止まらない）", height=100)

if st.button("知恵を借りる", type="primary"):
    if not api_key:
        st.error("サイドバーにGemini API Keyを入力してください。")
    elif not query:
        st.warning("相談内容を入力してください。")
    else:
        try:
            # Geminiの設定
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('models/gemini-2.5-flash') # 高速で賢いモデル

            with st.spinner('Geminiが古典を紐解き、市場を分析しています...'):
                # AIへのリクエスト
                response = model.generate_content(SYSTEM_PROMPT + f"\n\n【ユーザーの悩み】: {query}")
                
                # 返ってきたテキストをJSONとして読み込む
                # （AIが余計な文字をつけることがあるのでクリーニング）
                text_response = response.text.strip().replace("```json", "").replace("```", "")
                result = json.loads(text_response)

            # --- 5. 結果の表示（UIは前回と同じ） ---
            col1, col2 = st.columns(2)

            # 左手：論語
            with col1:
                st.markdown("### 📘 左手に論語（哲学）")
                st.info(f"**{result['rongo']['title']}**")
                st.markdown(f"### 「{result['rongo']['text']}」")
                st.caption(f"**現代語訳・解釈：** {result['rongo']['meaning']}")

            # 右手：算盤
            with col2:
                st.markdown("### 🧮 右手に算盤（実利）")
                st.success(f"**{result['soroban']['title']}**")
                st.markdown(f"**{result['soroban']['text']}**")
                st.write(f"👉 **Next Action:** {result['soroban']['action']}")

            # 統合メッセージ
            st.markdown("---")
            st.subheader("💡 統合された視点")
            st.write(result['synthesis'])

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.caption("APIキーが正しいか、またはAIがJSON形式以外で返答した可能性があります。もう一度押してみてください。")