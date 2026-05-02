import streamlit as st
import random
from database import save_review_status  # コメントアウトを解除して有効化

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
    # ユーザー名を取得（認証システムからセッションに保存されている名前）
    username = st.session_state.get("username", "guest")

    if st.session_state.show_explanation:
        with st.expander("📖 解説をチェック", expanded=True):
            st.write(q["explanation"])
            
            # --- ここからボタンエリア ---
            st.markdown("---")
            
            if mode == "見直しリスト":
                # 見直しリストモードでは、克服ボタンを表示
                if st.button("✨ 克服した！（リストから削除）", use_container_width=True, key=f"fix_{q['id']}"):
                    # データベースから削除を実行
                    save_review_status(username, q['id'], False)
                    st.toast("見直しリストから削除しました！")
                    
                    st.session_state.current_question = None
                    st.session_state.show_explanation = False
                    st.session_state.last_result = None
                    st.rerun()
            else:
                # 通常学習モードでは、追加/解除を切り替え
                is_review = q.get('review') == 1
                
                if is_review:
                    btn_label = "✅ 見直しリストに追加済み（解除する）"
                else:
                    btn_label = "🚩 見直しリストに追加"

                if st.button(btn_label, use_container_width=True, key=f"rev_btn_{q['id']}"):
                    # 現在のフラグを反転させてDBに保存
                    new_status = not is_review
                    save_review_status(username, q['id'], new_status)
                    
                    # メモリ上のデータも更新（即時反映用）
                    q['review'] = 1 if new_status else 0
                    
                    if new_status:
                        st.toast("見直しリストに追加しました！")
                    else:
                        st.toast("見直しリストから外しました。")
                    st.rerun()

                # 次の問題へボタン
                if st.button("次の問題へ ➡️", type="primary", use_container_width=True, key=f"next_{q['id']}"):
                    st.session_state.count += 1
                    st.session_state.current_question = random.choice(filtered_data)
                    st.session_state.show_explanation = False
                    st.session_state.last_result = None
                    st.rerun()