import pandas as pd
import streamlit as st

@st.cache_data
def load_data(file_path='quiz_data.csv'):
    try:
        # id列を文字列(str)として読み込むことで、2016-12-5などが日付になるのを防ぐ
        df = pd.read_csv(file_path, encoding='utf-8-sig', dtype={'id': str})
        
        # 'review'列がCSVにない場合は、初期値0（見直し不要）で作成する
        if 'review' not in df.columns:
            df['review'] = 0
            
        data = []
        for _, row in df.iterrows():
            # opt1～opt4までをリスト化
            options = [str(row[f'opt{i}']) for i in range(1, 5) if pd.notna(row.get(f'opt{i}'))]
            data.append({
                "id": str(row.get('id', '不明')),
                "type": str(row.get('type', '四肢択一')),
                "year": str(row.get('year', '不明')),
                "category": str(row.get('category', '未分類')),
                "question": str(row['question']),
                "answer": str(row['answer']),
                "explanation": str(row.get('explanation', '解説なし')),
                "options": options,
                "review": int(row.get('review', 0)) # 見直しフラグを読み込む
            })
        return data
    except Exception as e:
        st.error(f"CSV読み込みエラー: {e}")
        return []

def save_review_status(quiz_id, is_review):
    """
    指定された問題IDの見直しフラグをCSVに書き込む関数
    """
    try:
        # CSVを読み込む（最新の状態を反映させるためキャッシュを通さない）
        df = pd.read_csv('quiz_data.csv', encoding='utf-8-sig', dtype={'id': str})
        
        if 'review' not in df.columns:
            df['review'] = 0
            
        # 対象のIDのreview列を更新 (1: 見直し対象, 0: 対象外)
        df.loc[df['id'] == quiz_id, 'review'] = 1 if is_review else 0
        
        # CSVへ上書き保存
        df.to_csv('quiz_data.csv', index=False, encoding='utf-8-sig')
        
        # Streamlitの読み込みキャッシュをリセットして、画面に反映させる
        st.cache_data.clear()
        
    except Exception as e:
        st.error(f"見直し状態の保存に失敗しました: {e}")