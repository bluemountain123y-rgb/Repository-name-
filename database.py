# database.py に追加・修正
import pandas as pd
import streamlit as st

def save_review_status(quiz_id, is_review):
    """見直しフラグをCSVに保存する"""
    df = pd.read_csv('quiz_data.csv', encoding='utf-8-sig', dtype={'id': str})
    
    # 'review'列がなければ作成（初期値は0:不要）
    if 'review' not in df.columns:
        df['review'] = 0
        
    # 指定したIDのreview列を更新 (1:見直し対象, 0:完了)
    df.loc[df['id'] == quiz_id, 'review'] = 1 if is_review else 0
    
    # CSVに上書き保存
    df.to_csv('quiz_data.csv', index=False, encoding='utf-8-sig')
    # キャッシュをクリアして最新状態を反映させる
    st.cache_data.clear()

# load_data関数内でも 'review' 列を読み込むように修正
# (data.appendする際に "review": int(row.get('review', 0)) を追加)