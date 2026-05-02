import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def render_review_chart(base_data):
    """
    app.pyから渡されたbase_data（現在の形式・見直し対象のみ）を集計して表示。
    サイドバーのリストと完全に同期させ、全カテゴリを固定表示します。
    """
    # 全カテゴリの定義と順序を固定
    all_categories = [
        "①コンクリート材料", "②コンクリート性質", "③環境・経年劣化", 
        "④配(調)合設計", "⑤製造・品質管理", "⑥施工", 
        "⑦特殊コンクリート", "⑧構造・設計・ひび割れ"
    ]
    
    # データが空の場合の処理
    if not base_data:
        y_values = [0] * len(all_categories)
    else:
        # DataFrameに変換して集計
        df = pd.DataFrame(base_data)
        counts = df['category'].value_counts()
        # all_categoriesの順番通りに数値を取得（データがなければ0）
        y_values = [int(counts.get(cat, 0)) for cat in all_categories]

    # グラフの作成（plotly.graph_objects を使用してより詳細に制御）
    fig = go.Figure(data=[
        go.Bar(
            x=all_categories,
            y=y_values,
            marker_color='#00c3ff',  # 鮮やかな青
            text=[f"{v}" if v > 0 else "" for v in y_values],  # 0より大きい場合のみ数字を表示
            textposition='outside',
            cliponaxis=False
        )
    ])

    # レイアウト設定
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=300,
        xaxis_tickangle=-45,
        yaxis=dict(
            title="問題数",
            dtick=1,            # 1刻みに固定
            tickformat='d',      # 整数表示
            gridcolor='rgba(255,255,255,0.1)',
            rangemode='nonnegative' # マイナスを表示しない
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        showlegend=False
    )

    # 表示（ツールバーを非表示にしてスッキリさせる）
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})