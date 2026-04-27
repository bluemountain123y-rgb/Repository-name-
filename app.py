import streamlit as st
import pandas as pd
import random

# --- ページ設定 ---
st.set_page_config(page_title="コンクリート試験対策アプリ", page_icon="🏗️", layout="centered")

# --- 1. データの読み込み関数 ---
@st.cache_data
def load_data():
    try:
        # Excelから書き出したCSVを読み込む
        # utf-8-sig を指定することで、Excel保存時の文字化けを防ぎます
        df = pd.read_csv('quiz_data.csv', encoding='utf-8-sig')
        
        data = []
        for _, row in df.iterrows():
            # 選択肢をリストにまとめる（空欄（NaN）は除外）
            options = []
            if pd.notna(row.get('opt1')): options.append(str(row['opt1']))
            if pd.notna(row.get('opt2')): options.append(str(row['opt2']))
            if pd.notna(row.get('opt3')): options.append(str(row['opt3']))
            if pd.notna(row.get('opt4')): options.append(str(row['opt4']))
            
            data.append({
                "id": str(row.get('id', '不明')),
                "type": str(row['type']),
                "year": str(row['year']),
                "category": str(row['category']),
                "question": str(row['question']),
                "answer": str(row['answer']),
                "explanation": str(row['explanation']),
                "options": options
            })
        return data
    except Exception as e:
        st.error(f"CSVファイルの読み取りに失敗しました。ファイル名や保存形式（CSV UTF-8）を確認してください。: {e}")
        return []

# データを読み込み
all_quiz_data = load_data()

# --- 2. セッション状態の初期化 ---
if "count" not in st.session_state: st.session_state.count = 0
if "correct" not in st.session_state: st.session_state.correct = 0
if "show_explanation" not in st.session_state: st.session_state.show_explanation = False
if "current_question" not in st.session_state: st.session_state.current_question = None
if "last_result" not in st.session_state: st.session_state.last_result = None

# --- 3. サイドバーの設定 ---
st.sidebar.title("🛠️ 出題設定")
q_type = st.sidebar.radio("出題形式", ["四肢択一", "一問一答"])

# 選択された形式（四肢択一 or 一問一答）のデータだけを抽出
base_data = [q for q in all_quiz_data if q['type'] == q_type]

# カテゴリと年度のリストを動的に作成
if base_data:
    categories = ["全カテゴリ"] + sorted(list(set([q['category'] for q in base_data])))
    all_years = ["すべて"] + sorted(list(set([q['year'] for q in base_data])), reverse=True)
else:
    categories = ["データなし"]
    all_years = ["すべて"]

selected_cat = st.sidebar.selectbox("カテゴリ", categories)
selected_year = st.sidebar.selectbox("出題年度", all_years)

if st.sidebar.button("記録をリセットして最初から", use_container_width=True):
    st.session_state.count = 0
    st.session_state.correct = 0
    st.session_state.current_question = None
    st.session_state.show_explanation = False
    st.session_state.last_result = None
    st.rerun()

# --- 4. データのフィルタリング ---
filtered_data = base_data
if selected_cat != "全カテゴリ":
    filtered_data = [q for q in filtered_data if q["category"] == selected_cat]
if selected_year != "すべて":
    filtered_data = [q for q in filtered_data if q["year"] == selected_year]

# 初回の問題セット
if st.session_state.current_question is None and filtered_data:
    st.session_state.current_question = random.choice(filtered_data)

# --- 5. メイン画面 ---
st.title(f"🏗️ {q_type}モード")

# 成績表示
score_rate = (st.session_state.correct / st.session_state.count * 100) if st.session_state.count > 0 else 0
st.write(f"📊 **現在の成績: {st.session_state.count}問中 {st.session_state.correct}問正解 ({score_rate:.0f}%)**")
st.divider()

if not filtered_data:
    st.info("条件に合う問題がデータ内に見つかりません。")
else:
    q = st.session_state.current_question
    # ID、年度、カテゴリを表示
    st.caption(f"ID: {q['id']} | {q['year']}年 | {q['category']}")
    st.subheader("問題")
    st.info(f"**{q['question']}**")
    
    # 正誤判定メッセージの表示
    if st.session_state.last_result == "correct":
        st.success("✨ 正解！")
    elif st.session_state.last_result == "wrong":
        st.error(f"❌ 不正解...（正解：{q['answer']}）")

    # 回答ボタンの生成
    for option in q['options']:
        disabled = st.session_state.show_explanation
        if st.button(option, use_container_width=True, disabled=disabled, key=option):
            # 文字列として比較
            if str(option).strip() == str(q["answer"]).strip():
                st.session_state.correct += 1
                st.session_state.last_result = "correct"
            else:
                st.session_state.last_result = "wrong"
            st.session_state.show_explanation = True
            st.rerun()
            
    # 解説表示
    if st.session_state.show_explanation:
        with st.expander("📝 解説をチェック", expanded=True):
            st.write(q["explanation"])
            if st.button("次の問題へ ➡️", type="primary", use_container_width=True):
                st.session_state.count += 1
                st.session_state.current_question = random.choice(filtered_data)
                st.session_state.show_explanation = False
                st.session_state.last_result = None
                st.rerun()
                