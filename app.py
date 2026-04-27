import streamlit as st
import random

# 2つのデータファイルを読み込む
try:
    from data_4 import quiz_data_4
except ImportError:
    quiz_data_4 = []
try:
    from data_1 import quiz_data_1
except ImportError:
    quiz_data_1 = []

st.set_page_config(page_title="コンクリート試験対策アプリ", layout="centered")

# --- 1. セッション状態の初期化（ここを一番上に持ってくるのがコツ！） ---
if "count" not in st.session_state:
    st.session_state.count = 0  # 解いた問題数
if "goal" not in st.session_state:
    st.session_state.goal = 10  # 目標問題数

# --- 2. サイドバーの設定 ---
st.sidebar.title("🛠️ 出題設定")

# 出題形式の選択
q_type = st.sidebar.radio("出題形式", ["四肢択一", "一問一答"])

# 目標問題数の設定
st.session_state.goal = st.sidebar.slider("今日の目標問題数", 5, 50, 10)

if q_type == "四肢択一":
    base_data = quiz_data_4
else:
    base_data = quiz_data_1

# カテゴリの選択
categories = ["全カテゴリ"] + [
    "①コンクリート用材料", "②コンクリートの性質", "③環境・経年による劣化",
    "④配（調）合設計", "⑤製造・品質管理", "⑥施工",
    "⑦特殊コンクリート", "⑧構造・設計・ひび割れ"
]
selected_cat = st.sidebar.selectbox("カテゴリ", categories)

# 年度の選択
all_years = sorted(list(set([str(q.get('year', '不明')) for q in base_data])), reverse=True)
selected_year = st.sidebar.selectbox("出題年度", ["すべて"] + all_years)

# リセットボタン
if st.sidebar.button("記録をリセットして最初から"):
    st.session_state.count = 0
    st.session_state.current_question = None
    st.session_state.show_explanation = False
    st.rerun()

# --- 3. データのフィルタリング ---
filtered_data = base_data
if selected_cat != "全カテゴリ":
    filtered_data = [q for q in filtered_data if q["category"] == selected_cat]
if selected_year != "すべて":
    filtered_data = [q for q in filtered_data if q.get("year") == selected_year]

# --- 4. メイン画面 ---
st.title(f"🏗️ {q_type}モード")

# 進捗バーの表示（変数の準備ができた後に実行）
progress = min(st.session_state.count / st.session_state.goal, 1.0)
st.progress(progress)
st.write(f"📈 進捗: {st.session_state.count} / {st.session_state.goal} 問完了")

if st.session_state.count >= st.session_state.goal:
    st.balloons()
    st.success(f"🏆 目標の{st.session_state.goal}問を達成しました！")

# 問題の選定
if "current_question" not in st.session_state or st.session_state.current_question is None:
    st.session_state.current_question = random.choice(filtered_data) if filtered_data else None
    st.session_state.show_explanation = False

if not filtered_data:
    st.info("条件に合う問題がまだ登録されていません。")
else:
    q = st.session_state.current_question
    st.caption(f"{q.get('year_number', '')} | {q['category']}")
    st.subheader("問題")
    st.info(q["question"])
    
    for option in q.get("options", []):
        if st.button(option, use_container_width=True):
            if option == q["answer"]:
                st.success("✨ 正解！")
            else:
                st.error(f"❌ 不正解...（正解：{q['answer']}）")
            st.session_state.show_explanation = True
            
    if st.session_state.show_explanation:
        st.markdown("---")
        st.markdown(f"**【解説】**\n{q['explanation']}")
        if st.button("次の問題へ ➡️", type="primary"):
            st.session_state.count += 1 # カウントアップ
            st.session_state.current_question = random.choice(filtered_data)
            st.session_state.show_explanation = False
            st.rerun()
            