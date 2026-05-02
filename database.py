import sqlite3
import pandas as pd
import streamlit as st

# --- データベース初期化 ---
def init_db():
    """ユーザーごとの見直しリストを保存するDBとテーブルを作成"""
    conn = sqlite3.connect('quiz_app.db')
    c = conn.cursor()
    # username と quiz_id の組み合わせで保存（重複は無視）
    c.execute('''CREATE TABLE IF NOT EXISTS user_reviews
                 (username TEXT, quiz_id TEXT, UNIQUE(username, quiz_id))''')
    conn.commit()
    conn.close()

@st.cache_data
def load_data(file_path='quiz_data.csv'):
    """CSVからクイズデータを読み込む（見直しフラグはここでは扱わない）"""
    try:
        # id列を文字列として読み込み
        df = pd.read_csv(file_path, encoding='utf-8-sig', dtype={'id': str})
        
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
        st.error(f"CSV読み込みエラー: {e}")
        return []

# --- 見直しリスト操作関数 ---

def add_to_review(username, quiz_id):
    """DBにユーザーと問題IDを紐づけて保存"""
    try:
        conn = sqlite3.connect('quiz_app.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO user_reviews (username, quiz_id) VALUES (?, ?)", (username, str(quiz_id)))
        conn.commit()
        conn.close()
        # キャッシュをクリアして画面反映を確実にする
        st.cache_data.clear()
    except Exception as e:
        st.error(f"保存エラー: {e}")

def remove_from_review(username, quiz_id):
    """DBから特定のユーザーの見直しデータを削除"""
    try:
        conn = sqlite3.connect('quiz_app.db')
        c = conn.cursor()
        c.execute("DELETE FROM user_reviews WHERE username = ? AND quiz_id = ?", (username, str(quiz_id)))
        conn.commit()
        conn.close()
        st.cache_data.clear()
    except Exception as e:
        st.error(f"削除エラー: {e}")

def get_user_review_ids(username):
    """特定のユーザーが登録している問題IDリストを取得"""
    try:
        conn = sqlite3.connect('quiz_app.db')
        c = conn.cursor()
        c.execute("SELECT quiz_id FROM user_reviews WHERE username = ?", (username,))
        ids = [row[0] for row in c.fetchall()]
        conn.close()
        return ids
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return []

# 初回実行時にテーブルを作成
init_db()