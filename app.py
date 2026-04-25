import streamlit as st
import random
from data import quiz_data

# アプリのタイトル
st.title("🔥 コンクリート主任技師試験対策アプリ")
st.write("過去問からランダムに出題します。サクッと勉強しましょう！")

# セッション状態（クイズの進行）を管理する
if 'current_question' not in st.session_state:
    st.session_state.current_question = random.choice(quiz_data)
    st.session_state.show_answer = False

# 問題を表示
q = st.session_state.current_question
st.info(f"【問題】\n\n{q['question']}")

# 答えるボタン
col1, col2 = st.columns(2)
with col1:
    if st.button("⭕ 正解（○）", use_container_width=True):
        st.session_state.show_answer = True
        st.session_state.user_answer = "○"
with col2:
    if st.button("❌ 不正解（×）", use_container_width=True):
        st.session_state.show_answer = True
        st.session_state.user_answer = "×"

# 正解と解説を表示
if st.session_state.show_answer:
    if st.session_state.user_answer == q['answer']:
        st.success("✨ 正解です！")
    else:
        st.error(f"判定：残念！答えは {q['answer']} です。")
    
    st.write(f"**【解説】**\n{q['explanation']}")
    
    # 次の問題へ進むボタン
    if st.button("次の問題へ"):
        st.session_state.current_question = random.choice(quiz_data)
        st.session_state.show_answer = False
        st.rerun()