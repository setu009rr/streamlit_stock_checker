import pandas as pd
import altair as alt
import streamlit as st
import yfinance as yf

st.title("米国株価可視化アプリ")
st.sidebar.write("""
# GAFA株価
本アプリは株価可視化ツールになります。以下のオプションから表示日数を指定できます
""")

st.sidebar.write("""
## 表示日数選択
""")

days = st.sidebar.slider('日数',1, 50, 20)

st.write(f"""
### 過去 **{days}**日間 のGAFAの株価
""")

@st.cache
def get_data(days, tikers):
    df = pd.DataFrame()
    for company in tikers.keys():
        hist = yf.Ticker(tikers[company]).history(period=f'{days}d')
        hist.index.strftime('%d %B %Y')
        hist.index.name = 'Date'
        hist = hist[['Close']]
        hist.columns = [company]
        hist =hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try:
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください',
        0.0, 3500.0,(0.0,3500.0)
    )

    tikers = {
        'apple': 'AAPL',
        'facebook':'FB',
        'google': 'GOOGL',
        'netflix': 'NFLX',
        'amazon': 'AMZN'
    }

    df = get_data(days, tikers)
    companies = st.multiselect(
        '会社名を指定ください。',
        list(df.index),
        ['google', 'amazon', 'facebook', 'apple']
    )

    if not companies:
        st.error('少なくとも一社は選んでください')
    else:
        data = df.loc[companies]
        st.write("### 株価(USD)", data.sort_index())
        # index番号もカラムに変換する
        data = data.T.reset_index()
        # 日付を主キーにし、データを並び変える
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'})
        # Altchartを使用し、表データを作成する
        chart = (
            alt.Chart(data)
                .mark_line(opacity=0.8, clip=True)
                .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color="Name:N"
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "想定外のエラーが発生"
    )
