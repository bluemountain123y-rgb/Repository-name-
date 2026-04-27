import streamlit as st
import pandas as pd
import random

# --- ページ設定 ---
st.set_page_config(page_title="コンクリート試験対策アプリ", page_icon="🏗️", layout="centered")

# --- 1. データの読み込み関数 ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('quiz_data.csv', encoding='utf-8-sig')
        data = []
        for _, row in df.iterrows():
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
        st.error(f"CSVエラー: {e}")
        return []

all_quiz_data = load_data()

# --- 2. セッション状態 ---
if "count" not in st.session_state: st.session_state.count = 0
if "correct" not in st.session_state: st.session_state.correct = 0
if "show_explanation" not in st.session_state: st.session_state.show_explanation = False
if "current_question" not in st.session_state: st.session_state.current_question = None
if "last_result" not in st.session_state: st.session_state.last_result = None

# --- 3. サイドバーの設定 ---
st.sidebar.title("🛠️ 出題設定")
q_type = st.sidebar.radio("出題形式", ["四肢択一", "一問一答"])

# スライダーで出題数を設定 (5問〜50問、5問刻み、初期値10問)
target_total = st.sidebar.slider("出題数を設定", min_value=5, max_value=50, value=10, step=5)

base_data = [q for q in all_quiz_data if q['type'] == q_type]

if st.sidebar.button("記録をリセットして最初から", use_container_width=True):
    st.session_state.count = 0
    st.session_state.correct = 0
    st.session_state.current_question = None
    st.session_state.show_explanation = False
    st.session_state.last_result = None
    st.rerun()

# --- 4. 進行状況の表示 ---
st.title(f"🏗️ {q_type}モード")

# 進捗バーの計算
progress_val = min(st.session_state.count / target_total, 1.0)
st.progress(progress_val)
st.write(f"📊 **進行状況: {st.session_state.count} / {target_total} 問完了**")
st.write(f"✅ **正解数: {st.session_state.correct}問**")
st.divider()

# --- 5. メイン画面の処理 ---
if not base_data:
    st.info("データが見つかりません。")
elif st.session_state.count >= target_total:
    st.balloons()
    st.success(f"🎉 設定した {target_total} 問が終了しました！お疲れ様です！")
    if st.button("もう一度挑戦する", type="primary"):
        st.session_state.count = 0
        st.session_state.correct = 0
        st.session_state.current_question = None
        st.rerun()
else:
    if st.session_state.current_question is None:
        st.session_state.current_question = random.choice(base_data)
    
    q = st.session_state.current_question
    st.caption(f"ID: {q['id']} | {q['year']}年 | {q['category']}")
    st.subheader("問題")
    st.info(f"**{q['question']}**")
    
    if st.session_state.last_result == "correct":
        st.success("✨ 正解！")
    elif st.session_state.last_result == "wrong":
        st.error(f"❌ 不正解...（正解：{q['answer']}）")

    for option in q['options']:
        if st.button(option, use_container_width=True, disabled=st.session_state.show_explanation, key=option):
            if str(option).strip() == str(q["answer"]).strip():
                st.session_state.correct += 1
                st.session_state.last_result = "correct"
            else:
                st.session_state.last_result = "wrong"
            st.session_state.show_explanation = True
            st.rerun()
            
    if st.session_state.show_explanation:
        with st.expander("📝 解説をチェック", expanded=True):
            st.write(q["explanation"])
            if st.button("次の問題へ ➡️", type="primary", use_container_width=True):
                st.session_state.count += 1
                st.session_state.current_question = random.choice(base_data)
                st.session_state.show_explanation = False
                st.session_state.last_result = None
                st.rerun()
                