import pandas as pd
import pandas_ta as ta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import pandas_ta as ta



def isPivot(candle, window,df):
    """
    function that detects if a candle is a pivot/fractal point
    args: candle index, window before and after candle to test if pivot
    returns: 1 if pivot high, 2 if pivot low, 3 if both and 0 default
    """
    if candle - window < 0 or candle + window >= len(df):
        return 0

    pivotHigh = 1
    pivotLow = 2
    for i in range(candle - window, candle + window + 1):
        if df.iloc[candle].low > df.iloc[i].low:
            pivotLow = 0
        if df.iloc[candle].high < df.iloc[i].high:
            pivotHigh = 0
    if (pivotHigh and pivotLow):
        return 3
    elif pivotHigh:
        return pivotHigh
    elif pivotLow:
        return pivotLow
    else:
        return 0

def pointpos(x):
    if x['isPivot']==2:
        return x['low']-1e-3
    elif x['isPivot']==1:
        return x['high']+1e-3
    else:
        return np.nan


def detect_structure(candle, backcandles, window,df):
    """
    Attention! window should always be greater than the pivot window! to avoid look ahead bias
    """
    if (candle <= (backcandles + window)) or (candle + window + 1 >= len(df)):
        return 0

    localdf = df.iloc[
              candle - backcandles - window:candle - window]  # window must be greater than pivot window to avoid look ahead bias
    highs = localdf[localdf['isPivot'] == 1].high.tail(3).values
    lows = localdf[localdf['isPivot'] == 2].low.tail(3).values
    levelbreak = 0
    zone_width = 0.001
    if len(lows) == 3:
        support_condition = True
        mean_low = lows.mean()
        for low in lows:
            if abs(low - mean_low) > zone_width:
                support_condition = False
                break
        if support_condition and (mean_low - df.loc[candle].close) > zone_width * 2:
            levelbreak = -1

    if len(highs) == 3:
        resistance_condition = True
        mean_high = highs.mean()
        for high in highs:
            if abs(high - mean_high) > zone_width:
                resistance_condition = False
                break
        if resistance_condition and (df.loc[candle].close - mean_high) > zone_width * 2:
            levelbreak = 1
    return levelbreak


def main():
    df = pd.read_csv(
        "/Users/pankajti/dev/git/wqu/capstone/research/breakout/EURUSD_Candlestick_1_Hour_BID_04.05.2003-15.04.2023.csv")
    df = df[df['volume'] != 0]
    df.reset_index(drop=True, inplace=True)

    df['EMA'] = ta.ema(df.close, length=150)
    df.tail()

    df = df[0:10000]

    print(df.head())
    ## Trend detection

    EMAsignal = [0] * len(df)
    backcandles = 15

    for row in range(backcandles, len(df)):
        upt = 1
        dnt = 1
        for i in range(row - backcandles, row + 1):
            if max(df.open[i], df.close[i]) >= df.EMA[i]:
                dnt = 0
            if min(df.open[i], df.close[i]) <= df.EMA[i]:
                upt = 0
        if upt == 1 and dnt == 1:
            EMAsignal[row] = 3
        elif upt == 1:
            EMAsignal[row] = 2
        elif dnt == 1:
            EMAsignal[row] = 1

    df['EMASignal'] = EMAsignal

    window = 10
    df['isPivot'] = df.apply(lambda x: isPivot(x.name, window,df), axis=1)
    df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)
    dfpl = df[7800:8000]
    # fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
    #                                      open=dfpl['open'],
    #                                      high=dfpl['high'],
    #                                      low=dfpl['low'],
    #                                      close=dfpl['close'])])
    #
    # fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
    #                 marker=dict(size=5, color="MediumPurple"),
    #                 name="pivot")
    # fig.update_layout(xaxis_rangeslider_visible=False)
    # fig.show()

    df['pattern_detected'] = df.apply(lambda row: detect_structure(row.name, backcandles=60, window=11,df=df), axis=1)
    print(df[df['pattern_detected'] != 0])
    df["Pred"]=df['pattern_detected']
    df['Ret'] = df.close.pct_change()


    df["Positions"] = np.where(df["Pred"] > 0, 1, -1)
    df["Strat_ret"] = df["Positions"].shift(1) * df["Ret"]
    df["Positions_L"] = df["Positions"].shift(1)
    df["Positions_L"][df["Positions_L"] == -1] = 0
    df["Strat_ret_L"] = df["Positions_L"] * df["Ret"]
    df["CumRet"] = df["Strat_ret"].expanding().apply(lambda x: np.prod(1 + x) - 1)
    df["CumRet_L"] = df["Strat_ret_L"].expanding().apply(lambda x: np.prod(1 + x) - 1)
    df["bhRet"] = df["Ret"].expanding().apply(lambda x: np.prod(1 + x) - 1)

    Final_Return_L = np.prod(1 + df["Strat_ret_L"]) - 1
    Final_Return = np.prod(1 + df["Strat_ret"]) - 1
    Buy_Return = np.prod(1 + df["Ret"]) - 1

    print("Strat Return Long Only =", Final_Return_L * 100, "%")
    print("Strat Return =", Final_Return * 100, "%")
    print("Buy and Hold Return =", Buy_Return * 100, "%")


if __name__ == '__main__':
    main()