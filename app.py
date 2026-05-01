import streamlit as st
import random
import streamlit_authenticator as stauth
import plotly.express as px  # グラフ用に新規追加
import pandas as pd         # グラフ用に新規追加
from database import load_data
from styles import apply_custom_css
import quiz_ui as ui # UIパーツ担当

# --- ページ設定 ---
st.set_page_config(page_title="コンクリート主任技士 試験対策", page_icon="🏗️", layout="centered")

# --- グラフ描画関数（全カテゴリ表示対応） ---
def render_review_chart(base_data):
    # 全カテゴリの定義（表示順を固定）
    all_categories = [
        "①コンクリート材料", "②コンクリート性質", "③環境・経年劣化", 
        "④配(調)合設計", "⑤製造・品質管理", "⑥施工", 
        "⑦特殊コンクリート", "⑧構造・設計・ひび割れ"
    ]
    
    # 全て0で初期化
    chart_dict = {cat: 0 for cat in all_categories}
    
    # データの集計
    if base_data:
        for q in base_data:
            cat = q.get('category')
            if cat in chart_dict:
                chart_dict[cat] += 1
    
    # DataFrame作成
    df_chart = pd.DataFrame({
        'カテゴリ': all_categories,
        '問題数': [chart_dict[cat] for cat in all_categories]
    })
    
    # Plotlyによる描画
    fig = px.bar(df_chart, x='カテゴリ', y='問題数', color_discrete_sequence=['#00c3ff'])
    
    fig.update_yaxes(dtick=1, tickformat='d')
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_tickangle=-45, # カテゴリ名が長いので斜めにする
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white")
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 1. ユーザー認証 ---
credentials = {
    "usernames": {
        "admin": {"name": "管理者", "password": "concrete2026"},
        "user01": {"name": "テストユーザー", "password": "guest456"}
    }
}
authenticator = stauth.Authenticate(credentials, "concrete_quiz_cookie", "auth_key", cookie_expiry_days=30)
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

    # --- 3. サイドバー設定 ---
    st.sidebar.markdown("### ⚙️ モード選択")
    mode = st.sidebar.radio("学習モード", ["通常学習", "見直しリスト"])
    
    st.sidebar.markdown("---")
    q_type = st.sidebar.radio("出題形式", ["四肢択一", "一問一答"])

    # データ抽出（モードと形式でフィルタ）
    if mode == "通常学習":
        base_data = [q for q in all_quiz_data if q['type'] == q_type]
    else:
        # 見直しリストモード
        base_data = [q for q in all_quiz_data if q.get('review') == 1 and q['type'] == q_type]

    # カテゴリ・年度フィルタ
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

    # --- 4. メインロジック ---
    if not filtered_data:
        if mode == "見直しリスト":
            st.info(f"現在、{q_type} の見直しリストは空です。")
            render_review_chart([]) # 空でもグラフ枠を表示
        else:
            st.info("条件に合う問題がありません。設定を確認してください。")
    else:
        if mode == "見直しリスト":
            # 【見直しモード】
            st.subheader("📊 カテゴリ別見直し状況")
            render_review_chart(base_data)
            
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
            # 【通常学習モード】
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

elif st.session_state["authentication_status"] is False:
    st.error("ユーザー名またはパスワードが正しくありません")