import plotly.express as px
import pandas as pd
import streamlit as st

def render_review_chart(base_data):
    all_categories = [
        "①コンクリート材料", "②コンクリート性質", "③環境・経年劣化", 
        "④配(調)合設計", "⑤製造・品質管理", "⑥施工", 
        "⑦特殊コンクリート", "⑧構造・設計・ひび割れ"
    ]
    chart_dict = {cat: 0 for cat in all_categories}
    
    if base_data:
        for q in base_data:
            cat = q.get('category')
            if cat in chart_dict:
                chart_dict[cat] += 1
    
    df_chart = pd.DataFrame({
        'カテゴリ': all_categories,
        '問題数': [chart_dict[cat] for cat in all_categories]
    })
    
    fig = px.bar(df_chart, x='カテゴリ', y='問題数', color_discrete_sequence=['#00c3ff'])
    fig.update_yaxes(dtick=1, tickformat='d')
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white")
    )
    st.plotly_chart(fig, use_container_width=True)
