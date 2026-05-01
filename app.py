import streamlit as st
import random
from database import load_data
from styles import apply_custom_css
import quiz_ui as ui
from auth_utils import get_authenticator
from charts import render_review_chart

# ページ設定
st.set_page_config(page_title="コンクリート主任技士 試験対策", page_icon="🏗️", layout="centered")

# 1. ユーザー認証
authenticator = get_authenticator()
authenticator.login(location='main')

if st.session_state["authentication_status"]:
    authenticator.logout(button_name="ログアウト", location="sidebar")
    apply_custom_css()
    all_quiz_data = load_data()

    # ヘッダー
    st.markdown('<p class="hero-title">コンクリート主任技士</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">試験対策システム</p>', unsafe_allow_html=True)

    # セッション状態初期化
    for key in ["count", "correct", "show_explanation", "current_question", "last_result"]:
        if key not in st.session_state:
            st.session_state[key] = 0 if key in ["count", "correct"] else None

    # 2. サイドバー制御
    st.sidebar.markdown("### ⚙️ モード選択")
    mode = st.sidebar.radio("学習モード", ["通常学習", "見直しリスト"])
    q_type = st.sidebar.radio("出題形式", ["四肢択一", "一問一答"])

    # データ抽出
    if mode == "通常学習":
        base_data = [q for q in all_quiz_data if q['type'] == q_type]
    else:
        base_data = [q for q in all_quiz_data if q.get('review') == 1 and q['type'] == q_type]

    # サイドバー：フィルタと目標
    # (※ここは少し長いので、さらに整理したい場合は filtered_data 取得も関数化できます)
    if base_data:
        cat_counts = {q['category']: sum(1 for x in base_data if x['category'] == q['category']) for q in base_data}
        cat_options = ["全カテゴリ"] + [f"{c} ({n}問)" for c, n in sorted(cat_counts.items())]
        selected_cat_display = st.sidebar.selectbox("📂 カテゴリ選択", cat_options)
        selected_cat = selected_cat_display.split(" (")[0]
        filtered_data = base_data if selected_cat == "全カテゴリ" else [q for q in base_data if q['category'] == selected_cat]
    else:
        filtered_data = []

    target_total = st.sidebar.slider("🎯 目標出題数", 5, 50, 10, 5)

    # 3. メインロジック（表示のみに集中）
    if not filtered_data:
        st.info("データがありません。")
        if mode == "見直しリスト": render_review_chart([])
    else:
        if mode == "見直しリスト":
            st.subheader("📊 カテゴリ別見直し状況")
            render_review_chart(base_data)
            # 個別見直しロジック... (ui関数を呼び出す)
            # ...中略...
        else:
            # 通常学習ロジック... (ui関数を呼び出す)
            # ...中略...

elif st.session_state["authentication_status"] is False:
    st.error("認証エラー")