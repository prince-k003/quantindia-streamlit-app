import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title='QuantIndia Research System',
    page_icon='📈',
    layout='wide'
)

st.title('QuantIndia Research System')
st.markdown('*PhD-level systematic quantitative investment prototype*')
st.markdown('---')

# Folder paths
APP_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(APP_DIR, '..'))

POSSIBLE_BACKTEST_DIRS = [
    os.path.join(APP_DIR, 'backtest_results'),
    os.path.join(REPO_ROOT, 'backtest_results')
]

POSSIBLE_NLP_DIRS = [
    os.path.join(APP_DIR, 'data', 'nlp'),
    os.path.join(REPO_ROOT, 'data', 'nlp')
]

def find_existing_file(possible_dirs, filename):
    for folder in possible_dirs:
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            return path
    return None

@st.cache_data(ttl=3600)
def load_backtest():
    possible_files = [
        'tsmom_all_symbols.csv',
        'tsmom_nifty_results.csv',
        'trade_log.csv'
    ]

    for filename in possible_files:
        file_path = find_existing_file(POSSIBLE_BACKTEST_DIRS, filename)

        if file_path is not None:
            df = pd.read_csv(file_path)

            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
            elif 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp')
            else:
                df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
                df = df.set_index(df.columns[0])

            return df, file_path

    return pd.DataFrame(), None

bt, loaded_file = load_backtest()

col1, col2, col3, col4 = st.columns(4)

return_col = None

if len(bt) > 0:
    if 'strategy_return' in bt.columns:
        return_col = 'strategy_return'
    elif 'portfolio_return' in bt.columns:
        return_col = 'portfolio_return'
    elif 'tsmom_return' in bt.columns:
        return_col = 'tsmom_return'

    if return_col is not None:
        returns = bt[return_col].dropna()

        ytd_ret = returns.resample('YE').apply(lambda x: (1 + x).prod() - 1).iloc[-1]
        sharpe = returns.mean() * 252 / (returns.std() * np.sqrt(252))
        cum = (1 + returns).cumprod()
        mdd = (cum / cum.cummax() - 1).min()

        col1.metric('YTD Return', f'{ytd_ret:.1%}')
        col2.metric('Sharpe Ratio', f'{sharpe:.2f}')
        col3.metric('Max Drawdown', f'{mdd:.1%}')
        col4.metric('Research Papers', '7')
    else:
        col1.metric('YTD Return', 'N/A')
        col2.metric('Sharpe Ratio', 'N/A')
        col3.metric('Max Drawdown', 'N/A')
        col4.metric('Research Papers', '7')
else:
    col1.metric('YTD Return', 'No data')
    col2.metric('Sharpe Ratio', 'No data')
    col3.metric('Max Drawdown', 'No data')
    col4.metric('Research Papers', '7')

st.subheader('Strategy Performance vs Nifty 50')

if len(bt) > 0 and return_col is not None:
    fig = go.Figure()

    cum_strat = (1 + bt[return_col].dropna()).cumprod()

    fig.add_trace(
        go.Scatter(
            x=cum_strat.index,
            y=cum_strat,
            name='QuantIndia Strategy',
            line=dict(color='#185FA5', width=2)
        )
    )

    fig.update_layout(
        height=350,
        template='plotly_white',
        xaxis_title='Date',
        yaxis_title='Cumulative Return'
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info('No backtest data found yet.')

st.subheader('Research Foundation')

papers = {
    'Moskowitz et al. (2012)': 'Time-Series Momentum - JFE',
    'Agarwalla et al. (2013)': 'Indian Four-Factor Model - IIMA',
    'Frazzini & Pedersen (2014)': 'Betting Against Beta - JFE',
    'Nelson (1991)': 'EGARCH Volatility - Econometrica',
    'Hamilton (1989)': 'Regime Switching - Econometrica',
    'Hurst (1951)': 'Fractal Market Analysis',
    'Carr & Wu (2009)': 'Volatility Risk Premium - JoF',
}

for paper, desc in papers.items():
    st.markdown(f'- **{paper}**: {desc}')

st.markdown('---')
st.subheader('Data Check')

if loaded_file is not None:
    st.success(f'Loaded backtest file: {loaded_file}')
    st.write('Columns found:', list(bt.columns))
    st.write('Rows found:', len(bt))
else:
    st.error('No backtest CSV file found.')
    st.write('Checked these folders:')
    for folder in POSSIBLE_BACKTEST_DIRS:
        st.code(folder)
