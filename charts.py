import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import re

def render_review_chart(base_data):
    """
    app.pyから渡されたbase_dataを集計。
    カッコの全角半角や文字のゆれを無視し、冒頭の番号（①〜⑧）で確実に集計します。
    """
    # X軸に並べる標準のカテゴリ（表示用）
    standard_categories = [
        "①コンクリート材料", "②コンクリート性質", "③環境・経年劣化", 
        "④配(調)合設計", "⑤製造・品質管理", "⑥施工", 
        "⑦特殊コンクリート", "⑧構造・設計・ひび割れ"
    ]
    
    # 番号リスト（①, ②, ...）
    numbers = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧"]
    
    y_values = [0] * len(standard_categories)

    if base_data:
        df = pd.DataFrame(base_data)
        # 各データのカテゴリ名から冒頭の番号だけを抽出してカウント
        # 例：「④配（調）合設計」→「④」
        df['num_prefix'] = df['category'].astype(str).str.extract(f'([{"".join(numbers)}])')
        counts = df['num_prefix'].value_counts()
        
        # 標準リストの番号と一致するものをマッピング
        for i, num in enumerate(numbers):
            y_values[i] = int(counts.get(num, 0))

    # グラフ描画
    fig = go.Figure(data=[
        go.Bar(
            x=standard_categories,
            y=y_values,
            marker_color='#00c3ff',
            text=[f"{v}" if v > 0 else "" for v in y_values],
            textposition='outside',
            cliponaxis=False
        )
    ])

    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=300,
        xaxis_tickangle=-45,
        yaxis=dict(
            dtick=1, 
            tickformat='d', 
            gridcolor='rgba(255,255,255,0.1)', 
            rangemode='nonnegative',
            range=[0, max(y_values) + 1] if any(y_values) else [0, 1]
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})