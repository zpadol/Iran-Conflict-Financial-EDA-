from matplotlib import pyplot as plt
import seaborn as sns
from proj_func import *
import plotly.express as px


def line_chart_eimi(df):
    fig = px.line(df, x=df.index, y="EIMI_Price", title="EIMI price fluctuation chart", markers=True, color_discrete_sequence=["darkblue"])
    fig.update_layout(xaxis = dict(title = "Date"), yaxis = dict(title = "EIMI price"))
    fig.add_vline(x = "2026-02-28", line_color = "red", line_dash = "dash")
    return fig

def line_chart_oil(df):
    fig = px.line(df, x=df.index, y="Oil_Price", title="Oil price fluctuation chart", markers=True, color_discrete_sequence=["darkslategray"])
    fig.update_layout(xaxis=dict(title="Date"), yaxis=dict(title="Oil price"))
    fig.add_vline(x="2026-02-28", line_color="red", line_dash="dash")
    return fig

def normalized(df):
    df_copy = normalize_price(df, ["EIMI_Price","Oil_Price"])
    fig = px.line(df_copy, x=df_copy.index, y=["EIMI_Price","Oil_Price"], color_discrete_sequence=["darkblue", "darkslategray"])
    return fig

def scatter_chart(df):
    fig = px.scatter(df, x="Oil_Price_pct_change", y = "EIMI_Price_pct_change", trendline = "ols", color_discrete_sequence=["darkblue"])
    fig.update_layout(
        title="Correlation: Oil vs EIMI (Daily Changes)",
        xaxis_title="Oil Price Change (%)",
        yaxis_title="EIMI Price Change (%)"
    )
    fig.update_traces(line_color="red", selector=dict(mode='lines'))
    return fig

def heatmap(df):
    plt.style.use('dark_background')
    df_pct = df.filter(like="pct")
    corr = df_pct.corr()
    fig, ax = plt.subplots(figsize=(10,8))
    plt.title("Correlation Heatmap")
    sns.heatmap(corr, annot=True, fmt=".2f", ax = ax, square = True, cmap = 'vlag', center=0, vmin = -1, vmax = 1, linewidths=1, linecolor="white")
    return fig

