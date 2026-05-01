import streamlit as st
import random
import streamlit_authenticator as stauth
from database import load_data, save_review_status
from styles import apply_custom_css
import quiz_ui as ui  # UIパーツをインポート

# --- ページ設定と認証は省略 (既存の通り) ---
# ... (認証完了後の処理から) ...

    # データの読み込み
 if st.session_state["authentication_status"]:
    # ↓ この行の先頭のスペースを上の行と合わせる
    all_quiz_data = load_data() 
    apply_custom_css()

    # --- 3. サイドバー (既存のロジック) ---
    # ... (mode, q_type, filtered_data の選定ロジックをここに置く) ...

    # --- 4. メインロジック ---
    if not filtered_data:
        st.info("条件に合う問題がありません。")
    else:
        if mode == "見直しリスト":
            st.subheader(f"📂 {selected_cat} の見直し問題")
            q_dict = {f"[{q['id']}] {q['question'][:30]}...": q for q in filtered_data}
            selected_key = st.selectbox("問題を選択", ["-- 選択してください --"] + list(q_dict.keys()))
            
            if selected_key != "-- 選択してください --":
                q = q_dict[selected_key]
                if st.session_state.current_question != q:
                    st.session_state.current_question = q
                    st.session_state.show_explanation = False
                    st.session_state.last_result = None

                ui.render_quiz_card(q)
                ui.handle_answer(q, "rev")
                ui.show_explanation_and_nav(q, mode)

        else:
            # 通常学習モード (結果表示などは省略)
            if st.session_state.count < target_total:
                # 進行状況表示...
                if st.session_state.current_question is None:
                    st.session_state.current_question = random.choice(filtered_data)
                
                q = st.session_state.current_question
                ui.render_quiz_card(q)
                ui.handle_answer(q, "std")
                ui.show_explanation_and_nav(q, mode, filtered_data)