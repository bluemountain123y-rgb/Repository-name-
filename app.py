import streamlit as st
import random
import streamlit_authenticator as stauth
from database import load_data, save_review_status  # save_review_statusを追加
from styles import apply_custom_css

# --- ページ設定 ---
st.set_page_config(page_title="コンクリート主任技士 試験対策", page_icon="🏗️", layout="centered")

# --- 1. ユーザー認証 ---
credentials = {
    "usernames": {
        "admin": {"name": "管理者", "password": "concrete2026"},
        "user01": {"name": "テストユーザー", "password": "guest456"}
    }
}
authenticator = stauth.Authenticate(credentials, "concrete_quiz_cookie", "auth_key", cookie_expiry_days=30)
authenticator.login(location='main')

# 認証状況の確認
if st.session_state["authentication_status"] == False:
    st.error("ユーザー名またはパスワードが正しくありません")
elif st.session_state["authentication_status"] == None:
    st.warning("ユーザー名とパスワードを入力してください")
elif st.session_state["authentication_status"]:
    # 🔓 ログイン成功後のエリア
    authenticator.logout(button_name="ログアウト", location="sidebar")
    name = st.session_state["name"]

    # デザイン適用
    apply_custom_css()
    
    # データの読み込み
    all_quiz_data = load_data()

    # ヘッダー表示
    st.markdown('<p class="hero-title">コンクリート主任技士</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">試験対策システム</p>', unsafe_allow_html=True)
    st.write(f"ようこそ、{name} さん。学習を始めましょう。")

    # --- 2. セッション状態の初期化 ---
    for key in ["count", "correct", "show_explanation", "current_question", "last_result"]:
        if key not in st.session_state:
            st.session_state[key] = 0 if key in ["count", "correct"] else None

    # --- 3. サイドバー設定（見直しモード切り替え） ---
    st.sidebar.markdown("### ⚙️ モード選択")
    mode = st.sidebar.radio("学習モード", ["通常学習", "見直しリスト"])
    
    # 出題形式の選択（どちらのモードでも選択可能にする）
    st.sidebar.markdown("---")
    q_type = st.sidebar.radio("出題形式", ["四肢択一", "一問一答"])

    if mode == "通常学習":
        base_data = [q for q in all_quiz_data if q['type'] == q_type]
    else:
        # 見直しフラグがあり、かつ選択中の出題形式に一致するもの
        base_data = [q for q in all_quiz_data if q.get('review') == 1 and q['type'] == q_type]
        st.sidebar.success(f"🚩 見直し対象({q_type}): {len(base_data)} 問")

# フィルタリング（カテゴリ・年度）
    if base_data:
        # カテゴリごとの問題数を集計して表示用リストを作成
        cat_counts = {}
        for q in base_data:
            cat = q['category']
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        
        # セレクトボックスの表示を「カテゴリ名 (〇問)」にする
        category_options = ["全カテゴリ"] + [f"{cat} ({count}問)" for cat, count in sorted(cat_counts.items())]
        selected_cat_display = st.sidebar.selectbox("📂 カテゴリ選択", category_options)
        
        # 実際のフィルタリング用に「(〇問)」を削ってカテゴリ名だけ取り出す
        selected_cat = selected_cat_display.split(" (")[0]
        
        years = ["全年度"] + sorted(list(set([q['year'] for q in base_data])), reverse=True)
        selected_year = st.sidebar.selectbox("📅 年度選択", years)
        
        filtered_data = base_data
        if selected_cat != "全カテゴリ": 
            filtered_data = [q for q in filtered_data if q['category'] == selected_cat]
        if selected_year != "全年度": 
            filtered_data = [q for q in filtered_data if q['year'] == selected_year]
    else:
        filtered_data = []

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
            st.info("見直しリストに問題がありません。正解に自信がない問題にフラグを立てましょう！")
        else:
            st.info("条件に合う問題がありません。設定を確認してください。")
    else:
        # 全問終了時
        if st.session_state.count >= target_total:
            st.balloons()
            st.markdown("<div class='q-card' style='text-align: center; border-color: #ff9f00;'>", unsafe_allow_html=True)
            st.title("🏆 お疲れ様でした！")
            score_rate = int((st.session_state.correct / target_total) * 100)
            col1, col2 = st.columns(2)
            col1.metric("正答率", f"{score_rate}%")
            col2.metric("正解数", f"{st.session_state.correct} / {target_total}")
            if st.button("もう一度挑戦する", type="primary", use_container_width=True):
                st.session_state.count = 0
                st.session_state.correct = 0
                st.session_state.current_question = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        else:
            # 進捗表示
            progress_val = min(st.session_state.count / target_total, 1.0)
            st.progress(progress_val)
            st.write(f"📊 **進行状況: {st.session_state.count} / {target_total} 問完了**")
            
            # 問題選定
            if st.session_state.current_question is None or st.session_state.current_question not in filtered_data:
                st.session_state.current_question = random.choice(filtered_data)
            
            q = st.session_state.current_question
            
            # 問題表示
            st.markdown(f'''
                <div class="q-card">
                    <small style="color: #888;">ID: {q["id"]} | {q["year"]} | {q["category"]}</small>
                    <h3>{q["question"]}</h3>
                </div>
            ''', unsafe_allow_html=True)
            
            # 正誤判定の表示
            if st.session_state.last_result == "correct": st.success("✨ 正解です！")
            elif st.session_state.last_result == "wrong": st.error(f"❌ 不正解... (正解: {q['answer']})")

            # 回答ボタン
            for option in q['options']:
                if st.button(option, use_container_width=True, key=f"btn_{option}"):
                    if option.strip() == q["answer"].strip():
                        st.session_state.correct += 1
                        st.session_state.last_result = "correct"
                    else:
                        st.session_state.last_result = "wrong"
                    st.session_state.show_explanation = True
                    st.rerun()
            
            # 解説と見直し登録
            if st.session_state.show_explanation:
                with st.expander("📖 解説をチェック", expanded=True):
                    st.write(q["explanation"])
                    
                    # 見直しボタン（モードによって役割を変える）
                    is_review = q.get('review') == 1
                    if mode == "通常学習":
                        btn_label = "✅ 見直しリストから外す" if is_review else "🚩 見直しリストに追加"
                        if st.button(btn_label, use_container_width=True):
                            save_review_status(q['id'], not is_review)
                            st.rerun()
                    else:
                        if st.button("✨ 克服した！（リストから削除）", use_container_width=True):
                            save_review_status(q['id'], False)
                            st.session_state.count += 1
                            st.session_state.current_question = None
                            st.session_state.show_explanation = False
                            st.session_state.last_result = None
                            st.rerun()

                    if st.button("次の問題へ ➡️", type="primary", use_container_width=True):
                        st.session_state.count += 1
                        st.session_state.current_question = random.choice(filtered_data)
                        st.session_state.show_explanation = False
                        st.session_state.last_result = None
                        st.rerun()