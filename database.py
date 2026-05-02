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

def get_user_review_ids(username):
    """特定のユーザーが登録している問題IDリストを取得"""
    try:
        conn = sqlite3.connect('quiz_app.db')
        c = conn.cursor()
        c.execute("SELECT quiz_id FROM user_reviews WHERE username = ?", (username,))
        ids = [str(row[0]) for row in c.fetchall()] # IDは文字列として扱う
        conn.close()
        return ids
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return []

@st.cache_data
def load_data(username=None, file_path='quiz_data.csv'):
    """
    CSVからクイズデータを読み込み、ユーザーの見直し状態と統合する。
    usernameが渡された場合、DBから見直し対象IDを取得してフラグを立てる。
    """
    try:
        # id列を文字列として読み込み
        df = pd.read_csv(file_path, encoding='utf-8-sig', dtype={'id': str})
        
        # 現在のユーザーの見直し対象IDリストを取得
        review_ids = get_user_review_ids(username) if username else []
        
        data = []
        for _, row in df.iterrows():
            q_id = str(row.get('id', '不明'))
            options = [str(row[f'opt{i}']) for i in range(1, 5) if pd.notna(row.get(f'opt{i}'))]
            
            data.append({
                "id": q_id,
                "type": str(row.get('type', '四肢択一')),
                "year": str(row.get('year', '不明')),
                "category": str(row.get('category', '未分類')),
                "question": str(row['question']),
                "answer": str(row['answer']),
                "explanation": str(row.get('explanation', '解説なし')),
                "options": options,
                # --- 重要：ここでDBの状態を反映させる ---
                "review": 1 if q_id in review_ids else 0
            })
        return data
    except Exception as e:
        st.error(f"CSV読み込みエラー: {e}")
        return []

# --- 見直しリスト操作関数 ---

def save_review_status(username, quiz_id, status):
    """
    quiz_ui.py から呼び出すための統一関数。
    status=Trueなら追加、Falseなら削除。
    """
    try:
        conn = sqlite3.connect('quiz_app.db')
        c = conn.cursor()
        if status:
            c.execute("INSERT OR IGNORE INTO user_reviews (username, quiz_id) VALUES (?, ?)", (username, str(quiz_id)))
        else:
            c.execute("DELETE FROM user_reviews WHERE username = ? AND quiz_id = ?", (username, str(quiz_id)))
        conn.commit()
        conn.close()
        # キャッシュをクリアして最新の状態を再読み込みさせる
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"保存エラー: {e}")
        return False

# 初回実行時にテーブルを作成
init_db()