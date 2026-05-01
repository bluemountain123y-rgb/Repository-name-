import streamlit as st
import random
from database import save_review_status

def render_quiz_card(q):
    """問題文を表示するカード"""
    st.markdown(f'''
        <div class="q-card">
            <small style="color: #888;">ID: {q["id"]} | {q["year"]} | {q["category"]}</small>
            <h3>{q["question"]}</h3>
        </div>
    ''', unsafe_allow_html=True)

def handle_answer(q, prefix):
    """回答ボタンの生成と判定"""
    for option in q['options']:
        if st.button(option, use_container_width=True, key=f"{prefix}_{q['id']}_{option}"):
            if option.strip() == q["answer"].strip():
                st.session_state.last_result = "correct"
                if prefix == "std":
                    st.session_state.correct += 1
            else:
                st.session_state.last_result = "wrong"
            st.session_state.show_explanation = True
            st.rerun()

    if st.session_state.last_result == "correct": st.success("✨ 正解です！")
    elif st.session_state.last_result == "wrong": st.error(f"❌ 不正解... (正解: {q['answer']})")

def show_explanation_and_nav(q, mode, filtered_data=None):
    """解説表示とボタン類"""
    if st.session_state.show_explanation:
        with st.expander("📖 解説をチェック", expanded=True):
            st.write(q["explanation"])
            
            if mode == "見直しリスト":
                if st.button("✨ 克服した！（リストから削除）", use_container_width=True):
                    save_review_status(q['id'], False)
                    st.session_state.current_question = None
                    st.session_state.show_explanation = False
                    st.session_state.last_result = None
                    st.rerun()
            else:
                is_review = q.get('review') == 1
                btn_label = "✅ 見直し解消" if is_review else "🚩 見直しリストに追加"
                if st.button(btn_label, use_container_width=True):
                    save_review_status(q['id'], not is_review)
                    st.rerun()

                if st.button("次の問題へ ➡️", type="primary", use_container_width=True):
                    st.session_state.count += 1
                    st.session_state.current_question = random.choice(filtered_data)
                    st.session_state.show_explanation = False
                    st.session_state.last_result = None
                    st.rerun()