import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def render_review_chart(base_data):
    """
    app.pyから渡されたbase_dataを集計。
    カテゴリ名の不一致を完全に防ぐため、データ内にあるカテゴリを優先して表示します。
    """
    # X軸に並べる標準の順序（表記ゆれ防止用）
    standard_categories = [
        "①コンクリート材料", "②コンクリート性質", "③環境・経年劣化", 
        "④配(調)合設計", "⑤製造・品質管理", "⑥施工", 
        "⑦特殊コンクリート", "⑧構造・設計・ひび割れ"
    ]
    
    if not base_data:
        # データが空なら全て0で表示
        y_values = [0] * len(standard_categories)
        display_labels = standard_categories
    else:
        # 1. データをDataFrameに
        df = pd.DataFrame(base_data)
        
        # 2. カテゴリごとに集計（空白除去してマッチング率を上げる）
        df['category'] = df['category'].str.strip()
        counts = df['category'].value_counts()
        
        # 3. 集計結果を標準カテゴリにマッピング
        y_values = []
        for cat in standard_categories:
            # 前方一致などで柔軟にカウント（「③環境」で始まればOKにする）
            count = 0
            for actual_cat, val in counts.items():
                if actual_cat.startswith(cat[:3]): # 「③環境」などの頭文字で判定
                    count = val
                    break
            y_values.append(int(count))
        display_labels = standard_categories

    # グラフ描画
    fig = go.Figure(data=[
        go.Bar(
            x=display_labels,
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
        yaxis=dict(dtick=1, tickformat='d', gridcolor='rgba(255,255,255,0.1)', rangemode='nonnegative'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})