import streamlit as st
import pandas as pd
import random

# --- ページ設定 ---
st.set_page_config(page_title="コンクリート試験対策アプリ", page_icon="🏗️", layout="centered")
# --- カスタムデザイン (CSS) ---
st.markdown("""
    <style>
    /* メイン背景とカードのデザイン */
    .stApp {
        background-color: #f8f9fa;
    }
    .main-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    /* ボタンのカスタマイズ */
    div.stButton > button {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        background-color: white;
        transition: all 0.3s ease;
        font-size: 16px;
        padding: 10px 20px;
    }
    div.stButton > button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
        background-color: #fff5f5;
        transform: translateY(-2px);
    }
    /* 正解・不正解の強調 */
    .result-text {
        font-weight: bold;
        font-size: 1.2rem;
        text-align: center;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_stdio=True)
    
# --- 1. データの読み込み関数 ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('quiz_data.csv', encoding='utf-8-sig')
        data = []
        for _, row in df.iterrows():
            options = []
            for i in range(1, 5):
                opt = row.get(f'opt{i}')
                if pd.notna(opt): options.append(str(opt))
            
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
if "count" not in st.session_state: st.session_state.count = 0
if "correct" not in st.session_state: st.session_state.correct = 0
if "show_explanation" not in st.session_state: st.session_state.show_explanation = False
if "current_question" not in st.session_state: st.session_state.current_question = None
if "last_result" not in st.session_state: st.session_state.last_result = None

# --- 3. サイドバーの設定 ---
st.sidebar.title("🛠️ 出題設定")

# 形式の選択
q_type = st.sidebar.radio("出題形式", ["四肢択一", "一問一答"])
base_data = [q for q in all_quiz_data if q['type'] == q_type]

# カテゴリ・年度の絞り込み機能
if base_data:
    # Excelから自動でリストを作成（例：①コンクリート用材料...など）
    categories = ["全カテゴリ"] + sorted(list(set([q['category'] for q in base_data])))
    years = ["全年度"] + sorted(list(set([q['year'] for q in base_data])), reverse=True)
    
    selected_cat = st.sidebar.selectbox("カテゴリで絞り込む", categories)
    selected_year = st.sidebar.selectbox("年度で絞り込む", years)
    
    # フィルタリング実行
    filtered_data = base_data
    if selected_cat != "全カテゴリ":
        filtered_data = [q for q in filtered_data if q['category'] == selected_cat]
    if selected_year != "全年度":
        filtered_data = [q for q in filtered_data if q['year'] == selected_year]
else:
    filtered_data = []

# 出題数の設定
target_total = st.sidebar.slider("出題数を設定", min_value=5, max_value=50, value=10, step=5)

# リセットボタン
if st.sidebar.button("記録をリセットして最初から", use_container_width=True):
    st.session_state.count = 0
    st.session_state.correct = 0
    st.session_state.current_question = None
    st.session_state.show_explanation = False
    st.session_state.last_result = None
    st.rerun()

# --- 4. 進行状況の表示 ---
st.title(f"🏗️ {q_type}モード")

if not filtered_data:
    st.info("条件に合う問題がありません。Excelのカテゴリ名を確認してください。")
else:
    # プログレスバー
    progress_val = min(st.session_state.count / target_total, 1.0)
    st.progress(progress_val)
    st.write(f"📊 **進行状況: {st.session_state.count} / {target_total} 問完了**")
    st.divider()

    # --- 5. メイン画面の処理 ---
    if st.session_state.count >= target_total:
        # リザルト画面
        st.balloons()
        st.title("🏆 Result")
        score_rate = int((st.session_state.correct / target_total) * 100)
        
        col1, col2 = st.columns(2)
        col1.metric("正答率", f"{score_rate}%")
        col2.metric("正解数", f"{st.session_state.correct} / {target_total}")
        
        if st.button("もう一度挑戦する", type="primary", use_container_width=True):
            st.session_state.count = 0
            st.session_state.correct = 0
            st.session_state.current_question = None
            st.rerun()
    else:
        # 出題中
        if st.session_state.current_question is None or st.session_state.current_question not in filtered_data:
            st.session_state.current_question = random.choice(filtered_data)
        
        q = st.session_state.current_question
        st.caption(f"ID: {q['id']} | {q['year']}年 | {q['category']}")
        st.subheader("問題")
        st.info(f"**{q['question']}**")
        
        if st.session_state.last_result == "correct":
            st.success("✨ 正解！")
        elif st.session_state.last_result == "wrong":
            st.error(f"❌ 不正解...（正解：{q['answer']}）")

        # ボタン生成
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
                    st.session_state.current_question = random.choice(filtered_data)
                    st.session_state.show_explanation = False
                    st.session_state.last_result = None
                    st.rerun()