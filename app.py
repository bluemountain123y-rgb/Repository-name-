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

# --- サイドバーの設定 ---
st.sidebar.title("🛠️ 出題設定")

# 1. 出題形式の選択
q_type = st.sidebar.radio("出題形式", ["四肢択一", "一問一答"])

# 2. 形式に応じて読み込むデータを切り替え
if q_type == "四肢択一":
    base_data = quiz_data_4
else:
    base_data = quiz_data_1

# 3. カテゴリの選択
categories = ["全カテゴリ"] + [
    "①コンクリート用材料", "②コンクリートの性質", "③環境・経年による劣化",
    "④配（調）合設計", "⑤製造・品質管理", "⑥施工",
    "⑦特殊コンクリート", "⑧構造・設計・ひび割れ"
]
selected_cat = st.sidebar.selectbox("カテゴリ", categories)

# 4. 年度の選択（base_dataから自動で年度リストを作成）
all_years = sorted(list(set([str(q.get('year', '不明')) for q in base_data])), reverse=True)
selected_year = st.sidebar.selectbox("出題年度", ["すべて"] + all_years)

# --- データのフィルタリング ---
filtered_data = base_data

if selected_cat != "全カテゴリ":
    filtered_data = [q for q in filtered_data if q["category"] == selected_cat]

if selected_year != "すべて":
    filtered_data = [q for q in filtered_data if q.get("year") == selected_year]

# --- セッション状態の初期化 ---
# 出題形式やカテゴリが変わったときのためにリセットボタンも設置
if "current_question" not in st.session_state or st.sidebar.button("問題をリセット"):
    st.session_state.current_question = random.choice(filtered_data) if filtered_data else None
    st.session_state.show_explanation = False

# --- メイン画面 ---
st.title(f"🏗️ {q_type}モード")

if not filtered_data:
    st.info("条件に合う問題がまだ登録されていません。")
else:
    q = st.session_state.current_question
    
    # 補足情報
    st.caption(f"{q.get('year_number', '')} | {q['category']}")
    
    st.subheader("問題")
    st.info(q["question"])
    
    # 回答ボタン（縦並び）
    options = q.get("options", [])
    for option in options:
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
            # 次の問題をランダムに選んでリロード
            st.session_state.current_question = random.choice(filtered_data)
            st.session_state.show_explanation = False
            st.rerun()