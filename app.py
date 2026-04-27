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

# --- ページ設定（タイトルを日本語に修正） ---
st.set_page_config(page_title="コンクリート試験対策アプリ", page_icon="🏗️", layout="centered")

# --- 1. セッション状態の初期化 ---
if "count" not in st.session_state:
    st.session_state.count = 0      # 挑んだ問題数
if "correct" not in st.session_state:
    st.session_state.correct = 0    # 正解した数
if "goal" not in st.session_state:
    st.session_state.goal = 10      # 目標
if "show_explanation" not in st.session_state:
    st.session_state.show_explanation = False
if "current_question" not in st.session_state:
    st.session_state.current_question = None

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
    st.session_state.correct = 0
    st.session_state.current_question = None
    st.session_state.show_explanation = False
    st.rerun()

# --- 3. データのフィルタリング ---
filtered_data = base_data
if selected_cat != "全カテゴリ":
    filtered_data = [q for q in filtered_data if q["category"] == selected_cat]
if selected_year != "すべて":
    filtered_data = [q for q in filtered_data if q.get("year") == selected_year]

# 問題の選定
if st.session_state.current_question is None and filtered_data:
    st.session_state.current_question = random.choice(filtered_data)

# --- 4. メイン画面 ---
st.title(f"🏗️ {q_type}モード")

# 進捗バーの表示
progress = min(st.session_state.count / st.session_state.goal, 1.0)
st.progress(progress)
st.write(f"📈 進捗: {st.session_state.count} / {st.session_state.goal} 問完了")

# --- 5. 目標達成時のリザルト表示 ---
if st.session_state.count >= st.session_state.goal:
    st.balloons()
    score = st.session_state.correct
    total = st.session_state.count
    rate = (score / total) * 100 if total > 0 else 0
    
    st.success(f"🏆 目標の{st.session_state.goal}問を達成しました！お疲れ様です！")
    
    # スコアをカード形式で表示
    col1, col2, col3 = st.columns(3)
    col1.metric("解答数", f"{total}問")
    col2.metric("正解数", f"{score}問")
    col3.metric("正解率", f"{rate:.0f}%")
    
    if rate >= 80:
        st.write("🌟 **素晴らしい！この調子で合格を掴みましょう！**")
    elif rate >= 60:
        st.write("👍 **安定しています。間違えた所を復習しましょう！**")
    else:
        st.write("📖 **伸びしろたっぷりです！繰り返し解いて知識を定着させよう！**")
        
    if st.button("もう一度挑戦する", type="primary"):
        st.session_state.count = 0
        st.session_state.correct = 0
        st.session_state.current_question = None
        st.rerun()

# --- 6. 問題表示エリア ---
elif not filtered_data:
    st.info("条件に合う問題がまだ登録されていません。")
else:
    q = st.session_state.current_question
    st.caption(f"{q.get('year_number', '')} | {q['category']}")
    st.subheader("問題")
    st.info(q["question"])
    
    # 回答ボタン
    for option in q.get("options", []):
        # 解答済みの場合はボタンを押せなくする
        disabled = st.session_state.show_explanation
        if st.button(option, use_container_width=True, disabled=disabled, key=option):
            if option == q["answer"]:
                st.success("✨ 正解！")
                st.session_state.correct += 1
            else:
                st.error(f"❌ 不正解...（正解：{q['answer']}）")
            st.session_state.show_explanation = True
            st.rerun()
            
    if st.session_state.show_explanation:
        st.markdown("---")
        st.markdown(f"**【解説】**\n{q['explanation']}")
        if st.button("次の問題へ ➡️", type="primary", use_container_width=True):
            st.session_state.count += 1
            st.session_state.current_question = random.choice(filtered_data)
            st.session_state.show_explanation = False
            st.rerun()
            