import streamlit as st
import random
from data import quiz_data

st.set_page_config(page_title="コンクリート試験対策", layout="centered")

# サイドバーでモード選択
st.sidebar.title("🛠️ メニュー")
mode = st.sidebar.radio("出題モード", ["全カテゴリからランダム", "カテゴリ別に解く"])
q_type = st.sidebar.radio("出題形式", ["四者択一", "〇×形式"])

# データのフィルタリング
filtered_data = [q for q in quiz_data if q["type"] == q_type]

if mode == "カテゴリ別に解く":
    categories = [
        "①コンクリート用材料", "②コンクリートの性質", "③環境・経年による劣化",
        "④配（調）合設計", "⑤製造・品質管理", "⑥施工",
        "⑦特殊コンクリート", "⑧構造・設計・ひび割れ"
    ]
    selected_cat = st.sidebar.selectbox("カテゴリを選択", categories)
    filtered_data = [q for q in filtered_data if q["category"] == selected_cat]

# セッション状態の初期化
if "current_question" not in st.session_state or st.sidebar.button("問題をリセット"):
    st.session_state.current_question = random.choice(filtered_data) if filtered_data else None
    st.session_state.show_explanation = False

st.title("🏗️ コンクリート試験対策")

if not filtered_data:
    st.info("現在、選択された条件に合う問題がありません。データを追加してください。")
else:
    q = st.session_state.current_question
    
    st.subheader(f"【{q['category']}】")
    st.info(q["question"])
    
    # 回答ボタンの表示
    cols = st.columns(len(q["options"]))
    for i, option in enumerate(q["options"]):
        if cols[i].button(option):
            if option == q["answer"]:
                st.success("✨ 正解！")
            else:
                st.error("❌ 不正解...")
            st.session_state.show_explanation = True
            
    if st.session_state.show_explanation:
        st.write(f"**【解説】** {q['explanation']}")
        if st.button("次の問題へ"):
            st.session_state.current_question = random.choice(filtered_data)
            st.session_state.show_explanation = False
            st.rerun()