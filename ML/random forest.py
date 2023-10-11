import yfinance as yf
import numpy as np
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import datetime as dt
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from yellowbrick.classifier import ConfusionMatrix
from sklearn.model_selection import train_test_split
from yellowbrick.classifier import ClassificationReport
from sklearn.metrics import confusion_matrix
import warnings

warnings.filterwarnings("ignore")


def main():
    end_date = dt.datetime.now().date()
    start_date = end_date - dt.timedelta(3650)
    prediction_duration = 30
    # start_date = None
    # end_date=None
    stock_name = 'TCS.NS'
    stock = yf.Ticker(stock_name).history(start=start_date, end=end_date, auto_adjust=False)
    run_model(prediction_duration, stock)


def run_model(prediction_duration, stock):
    training_data = pd.DataFrame()
    training_data['close'] = stock[['Adj Close']]
    sm = training_data.ta.sma(append=True)
    rs = training_data.ta.rsi(append=True)
    df = create_output_field(prediction_duration, training_data)

    X = df.iloc[:, 2:4]
    y = df.iloc[:, -1]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)
    classifier = RandomForestClassifier()
    classifier.fit(X, y)
    classifier.score(X, y)
    y_pred = classifier.predict(X)
    confusion_matrix(y, y_pred)
    classifier = RandomForestClassifier()
    classifier.fit(X_train, y_train)
    y_pred = classifier.predict(X_test)
    print(confusion_matrix(y_test, y_pred))
    model = classifier
    print("check result for model ")
    result = model_position_performance(df, model)
    print("check result for dummy  model ")
    dummy_model = DummyClassifier(strategy="most_frequent")
    dummy_model.fit(X_train, y_train)
    result = model_position_performance(df, dummy_model)


def create_output_field(prediction_duration, training_data):
    df = training_data
    df["Ret"] = df["close"].pct_change()
    df.reset_index(inplace=True)
    name = "Ret"
    ret_fieldi = f"Ret{prediction_duration}_i"
    ret_field = f"Ret{prediction_duration}"
    df[ret_fieldi] = df[name].rolling(prediction_duration).apply(lambda x: 100 * (np.prod(1 + x / 100) - 1))
    df[ret_field] = df[ret_fieldi].shift(-prediction_duration)
    df["Output"] = df[ret_field].apply(lambda x: 1 if x > 0 else -1)
    df["Output"] = df["Output"].astype(int)
    del df[ret_field]
    df = df.dropna()
    return df


def model_position_performance(df, model):
    df['Pred'] = model.predict(df[['SMA_10', 'RSI_14']])
    df["Positions"] = np.where(df["Pred"] > 0.5, 1, -1)
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
    df = df.dropna()
    ret = df.CumRet_L
    print(f"sharpe for CumRet_L  {ret.mean() / ret.std()}")
    ret = df.bhRet
    print(f"sharpe for bhRet  {ret.mean() / ret.std()}")
    ret = df.CumRet
    print(f"sharpe for CumRet  {ret.mean() / ret.std()}")
    return df


if __name__ == '__main__':
    main()