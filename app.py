import streamlit as st
import random
from database import load_data  # 存在する関数のみをインポート
from styles import apply_custom_css
import quiz_ui as ui
from auth_utils import get_authenticator
from charts import render_review_chart

# --- ページ設定 ---
st.set_page_config(page_title="コンクリート主任技士 試験対策", page_icon="🏗️", layout="centered")

# --- 1. ユーザー認証 ---
authenticator = get_authenticator()
authenticator.login(location='main')

if st.session_state["authentication_status"]:
    # 🔓 ログイン成功時の処理
    authenticator.logout(button_name="ログアウト", location="sidebar")
    apply_custom_css()
    all_quiz_data = load_data()

    # ヘッダー表示
    st.markdown('<p class="hero-title">コンクリート主任技士</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">試験対策システム</p>', unsafe_allow_html=True)

    # セッション状態の初期化
    for key in ["count", "correct", "show_explanation", "current_question", "last_result"]:
        if key not in st.session_state:
            st.session_state[key] = 0 if key in ["count", "correct"] else None

    # --- 2. サイドバー制御 ---
    st.sidebar.markdown("### ⚙️ モード選択")
    mode = st.sidebar.radio("学習モード", ["通常学習", "見直しリスト"])
    st.sidebar.markdown("---")
    q_type = st.sidebar.radio("出題形式", ["四肢択一", "一問一答"])

    # データ抽出の基礎（モードと形式でフィルタ）
    if mode == "通常学習":
        base_data = [q for q in all_quiz_data if q['type'] == q_type]
    else:
        # 見直しリストモード：reviewフラグが1かつ形式が一致するもの
        base_data = [q for q in all_quiz_data if q.get('review') == 1 and q['type'] == q_type]

    # カテゴリ・フィルタ処理
    if base_data:
        cat_counts = {q['category']: sum(1 for x in base_data if x['category'] == q['category']) for q in base_data}
        cat_options = ["全カテゴリ"] + [f"{c} ({n}問)" for c, n in sorted(cat_counts.items())]
        selected_cat_display = st.sidebar.selectbox("📂 カテゴリ選択", cat_options)
        selected_cat = selected_cat_display.split(" (")[0]
        
        filtered_data = base_data
        if selected_cat != "全カテゴリ":
            filtered_data = [q for q in filtered_data if q['category'] == selected_cat]
    else:
        filtered_data = []

    # 共通設定
    st.sidebar.markdown("---")
    target_total = st.sidebar.slider("🎯 目標出題数", 5, 50, 10, 5)
    
    if st.sidebar.button("🔄 記録をリセット", use_container_width=True):
        st.session_state.count = 0
        st.session_state.correct = 0
        st.session_state.current_question = None
        st.session_state.show_explanation = False
        st.session_state.last_result = None
        st.rerun()

    # --- 3. メインロジック ---
    if not filtered_data:
        if mode == "見直しリスト":
            st.info(f"現在、{q_type} の見直しリストは空です。")
            render_review_chart([])  # 空の状態でもグラフ枠（0問表示）を出す
        else:
            st.info("条件に合う問題がありません。設定を確認してください。")
    else:
        if mode == "見直しリスト":
            # 【見直しモード：グラフと個別選択】
            st.subheader("📊 カテゴリ別見直し状況")
            render_review_chart(base_data)  # charts.pyの関数を使用
            
            st.markdown("---")
            st.subheader(f"📂 {selected_cat} の個別見直し")
            
            q_dict = {f"[{q['id']}] {q['question'][:30]}...": q for q in filtered_data}
            selected_key = st.selectbox("解きたい問題を選択", ["-- 選択してください --"] + list(q_dict.keys()))
            
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
            # 【通常学習モード：進行バー付き】
            if st.session_state.count >= target_total:
                st.balloons()
                st.success("🏆 目標達成！お疲れ様でした。")
                st.metric("正答率", f"{int((st.session_state.correct / target_total) * 100)}%")
                if st.button("もう一度最初から挑戦", use_container_width=True):
                    st.session_state.count = 0
                    st.session_state.correct = 0
                    st.session_state.current_question = None
                    st.rerun()
            else:
                progress_val = min(st.session_state.count / target_total, 1.0)
                st.progress(progress_val)
                st.write(f"📊 **進行状況: {st.session_state.count} / {target_total} 問完了**")

                if st.session_state.current_question is None:
                    st.session_state.current_question = random.choice(filtered_data)
                
                q = st.session_state.current_question
                ui.render_quiz_card(q)
                ui.handle_answer(q, "std")
                ui.show_explanation_and_nav(q, mode, filtered_data)

# --- 認証エラー時の表示 ---
elif st.session_state["authentication_status"] is False:
    st.error("ユーザー名またはパスワードが正しくありません")