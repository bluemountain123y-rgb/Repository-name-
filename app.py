import streamlit as st
import pandas as pd
import random
import streamlit_authenticator as stauth

# --- ページ設定 ---
st.set_page_config(page_title="コンクリート主任技士 試験対策", page_icon="🏗️", layout="centered")

# --- 1. ユーザー認証の設定 ---
names = ["管理者", "テストユーザー"]
usernames = ["admin", "user01"]
# ★ここにご自身のハッシュ($2b$12$...)を貼り付けてください
hashed_passwords = [
    'concrete2026', 
    'guest456'
] 

authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords,
    "concrete_quiz_cookie", "auth_key", cookie_expiry_days=30
)

# ログイン画面を出す
name, authentication_status, username = authenticator.login("ログイン", "main")

if authentication_status == False:
    st.error("ユーザー名またはパスワードが正しくありません")
elif authentication_status == None:
    st.warning("ユーザー名とパスワードを入力してください")
elif authentication_status:
    # 🔓 ここから下はすべてログイン成功後のみ実行されるため、段落を右に下げます
    
    authenticator.logout("ログアウト", "sidebar")

    # --- 🎨 サイバー・コンクリート・デザイン ---
    st.markdown("""
        <style>
        .stApp {
            background-color: #2b2b2b;
            background-image: 
                radial-gradient(#3a3a3a 15%, transparent 16%),
                radial-gradient(#3a3a3a 15%, transparent 16%),
                linear-gradient(#2b2b2b 0%, #333333 100%);
            background-size: 100px 100px, 100px 100px, 100% 100%;
            background-position: 0 0, 50px 50px, 0 0;
            color: #e0e0e0;
        }
        .hero-title {
            font-size: 3.5rem !important; 
            font-weight: 900;
            color: #fff;
            text-align: center;
            text-shadow: 0 0 20px #00c3ff, 0 0 40px #00c3ff;
            margin-top: 20px;
            margin-bottom: 0px;
            line-height: 1.1;
        }
        .hero-subtitle {
            font-size: 1.2rem;
            color: #00c3ff;
            text-align: center;
            margin-bottom: 40px;
            font-weight: bold;
            letter-spacing: 5px;
        }
        .q-card {
            padding: 25px;
            border-radius: 15px;
            background: rgba(40, 40, 40, 0.85);
            border: 2px solid #00c3ff;
            box-shadow: 0 0 20px rgba(0, 195, 255, 0.4);
            margin-bottom: 25px;
        }
        .q-card h3 {
            font-size: 1.3rem !important;
            color: #fff;
            line-height: 1.6;
            font-weight: 500;
        }
        div.stButton > button {
            border-radius: 8px;
            border: 1px solid #00c3ff;
            background: rgba(0, 195, 255, 0.1) !important;
            color: #00c3ff !important;
            font-weight: bold;
        }
        div.stButton > button:hover {
            background: rgba(0, 195, 255, 0.3) !important;
            box-shadow: 0 0 15px rgba(0, 195, 255, 0.8);
        }
        .stProgress > div > div > div > div {
            background-color: #00c3ff;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<p class="hero-title">コンクリート主任技士</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">試験対策システム</p>', unsafe_allow_html=True)
    st.write(f"ようこそ、{name} さん。学習を始めましょう。")

    # --- 1. データの読み込み ---
    @st.cache_data
    def load_data():
        try:
            df = pd.read_csv('quiz_data.csv', encoding='utf-8-sig')
            data = []
            for _, row in df.iterrows():
                options = [str(row[f'opt{i}']) for i in range(1, 5) if pd.notna(row.get(f'opt{i}'))]
                data.append({
                    "id": str(row.get('id', '不明')),
                    "type": str(row.get('type', '四肢択一')),
                    "year": str(row.get('year', '不明')),
                    "category": str(row.get('category', '未分類')),
                    "question": str(row['question']),
                    "answer": str(row['answer']),
                    "explanation": str(row.get('explanation', '解説なし')),
                    "options": options
                })
            return data
        except Exception as e:
            st.error(f"CSVエラー: {e}")
            return []

    all_quiz_data = load_data()

    # --- 2. セッション状態 ---
    for key in ["count", "correct", "show_explanation", "current_question", "last_result"]:
        if key not in st.session_state:
            st.session_state[key] = 0 if key in ["count", "correct"] else None

    # --- 4. サイドバー設定 ---
    st.sidebar.markdown("### ⚙️ 出題設定")
    q_type = st.sidebar.radio("出題形式", ["四肢択一", "一問一答"])
    base_data = [q for q in all_quiz_data if q['type'] == q_type]

    if base_data:
        categories = ["全カテゴリ"] + sorted(list(set([q['category'] for q in base_data])))
        years = ["全年度"] + sorted(list(set([q['year'] for q in base_data])), reverse=True)
        selected_cat = st.sidebar.selectbox("📂 カテゴリ選択", categories)
        selected_year = st.sidebar.selectbox("📅 年度選択", years)
        
        filtered_data = base_data
        if selected_cat != "全カテゴリ": filtered_data = [q for q in filtered_data if q['category'] == selected_cat]
        if selected_year != "全年度": filtered_data = [q for q in filtered_data if q['year'] == selected_year]
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

    # --- 5. メインロジック ---
    if not filtered_data:
        st.info("条件に合う問題がありません。設定を確認してください。")
    else:
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
            # 進捗
            progress_val = min(st.session_state.count / target_total, 1.0)
            st.progress(progress_val)
            st.write(f"📊 **進行状況: {st.session_state.count} / {target_total} 問完了**")
            
            if st.session_state.current_question is None or st.session_state.current_question not in filtered_data:
                st.session_state.current_question = random.choice(filtered_data)
            
            q = st.session_state.current_question
            
            # 問題カード
            st.markdown(f'<div class="q-card"><small style="color: #888;">ID: {q["id"]} | {q["year"]} | {q["category"]}</small><h3>{q["question"]}</h3></div>', unsafe_allow_html=True)
            
            if st.session_state.last_result == "correct": st.success("✨ 正解です！")
            elif st.session_state.last_result == "wrong": st.error(f"❌ 不正解... (正解: {q['answer']})")

            for option in q['options']:
                if st.button(option, use_container_width=True, key=option):
                    if option.strip() == q["answer"].strip():
                        st.session_state.correct += 1
                        st.session_state.last_result = "correct"
                    else:
                        st.session_state.last_result = "wrong"
                    st.session_state.show_explanation = True
                    st.rerun()
                    
            if st.session_state.show_explanation:
                with st.expander("📖 解説をチェック", expanded=True):
                    st.write(q["explanation"])
                    if st.button("次の問題へ ➡️", type="primary", use_container_width=True):
                        st.session_state.count += 1
                        st.session_state.current_question = random.choice(filtered_data)
                        st.session_state.show_explanation = False
                        st.session_state.last_result = None
                        st.rerun()