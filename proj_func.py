from functools import reduce, partial
import pandas as pd
import yfinance as yf
from scipy import stats

def download_market(params):
    """
    (PL) Pobiera historyczne dane rynkowe dla podanego symbolu i zakresu dat z Yahoo Finance.
    (EN) Fetches historical market data for a given ticker and date range from Yahoo Finance.
    """
    ticker, start, end = params
    return yf.download(ticker, start=start, end=end)

def clean_data(data, name):
    """
    (PL) Wybiera ceny zamknięcia, formatuje daty do RRRR-MM-DD i ustawia je jako indeks.
    (EN) Extracts 'Close' prices, formats dates to YYYY-MM-DD, and sets them as the index.
    """
    data = data["Close"].reset_index()
    data.columns = ['date', name]
    data['date'] = pd.to_datetime(data['date']).dt.date
    data.set_index('date', inplace=True)
    return data


def normalize_price(df, cols):
    """
    (PL) Normalizuje ceny, przyjmując pierwszą wartość jako bazę 100. Obsługuje jedną kolumnę lub listę.
    (EN) Normalizes prices by setting the first value as base 100. Supports single column or list.
    """
    df_copy = df.copy()
    if isinstance(cols, str):
        cols = [cols]

    for col in cols:
        base_value = df_copy[col].iloc[0]
        if base_value != 0:
            df_copy[col] = (df_copy[col] / base_value) * 100

    return df_copy

def total_change(df, col):
    """
    (PL) Oblicza całkowitą procentową zmianę wartości między pierwszym a ostatnim wpisem.
    (EN) Calculates the total percentage change between the first and last entry.
    """
    first, last = df[col].iloc[0], df[col].iloc[-1]
    change = ((last - first) / first) * 100
    return float(change)

def pct_change(df, col):
    """
    (PL) Oblicza dzienną procentową zmianę wartości (okres do okresu).
    (EN) Calculates period-to-period percentage changes.
    """
    df_copy = df.copy()
    df_copy[f"{col}_pct_change"] = df_copy[col].pct_change() * 100
    return df_copy

def ext_pct_change(df, col):
    """
    (PL) Identyfikuje daty oraz wartości dla ekstremów (maksimum i minimum) w szeregu.
    (EN) Identifies dates and values for extremes (maximum and minimum) in a time series.
    """
    max_date, min_date = df[col].idxmax(), df[col].idxmin()
    return {
        "max_date": max_date,
        "max_value": df.loc[max_date, col],
        "min_date": min_date,
        "min_value": df.loc[min_date, col]
    }

def color_delta(val):
    """
    (PL) Zwraca styl CSS: czerwony dla wartości ujemnych, zielony dla dodatnich.
    (EN) Returns CSS styling: red for negative values, green for positive values.
    """
    if val < 0: return 'color: red;'
    elif val > 0: return 'color: green;'
    return ''

def lin_reg(df, x, y):
    """
    (PL) Przeprowadza analizę regresji liniowej i zwraca statystyki modelu.
    (EN) Performs linear regression and returns key model statistics.
    """
    df_clean = df.dropna()
    slope, intercept, rvalue, pvalue, stderr = stats.linregress(df_clean[x], df_clean[y])
    return {
        "slope": slope, "intercept": intercept,
        "rvalue": rvalue, "pvalue": pvalue, "stderr": stderr
    }

def roi_calc(df_col, amount):
    """
    (PL) Oblicza skumulowany wzrost początkowej kwoty inwestycji na podstawie stóp zwrotu.
    (EN) Calculates the cumulative growth of an initial investment based on returns.
    """
    return (1 + (df_col / 100)).cumprod() * amount

def compose(*funcs):
    """
    (PL) Składa wiele funkcji w jeden potok (pipeline) wykonujący się od prawej do lewej.
    (EN) Composes multiple functions into a single pipeline executing from right to left.
    """
    return lambda initial: reduce(lambda acc, f: f(acc), reversed(funcs), initial)

def get_merged_assets(assets_config, start, end):
    """
    (PL) Pobiera wiele aktywów i łączy je w jedną tabelę.
    (EN) Fetches multiple assets and merges them into a single table.
    """
    dfs = [
        compose(
            partial(clean_data, name=name),
            download_market
        )((ticker, start, end))
        for ticker, name in assets_config
    ]

    return reduce(
        lambda left, right: pd.merge(
            left, right, left_index=True, right_index=True, how='inner'
        ),
        dfs
    )

def asset_pipeline_norm(name):
    """
    (PL) Tworzy potok: Pobierz -> Wyczyść -> Oblicz % zmiany.
    (EN) Pipeline: Fetches -> Cleans -> -> Calculates %
    """
    return compose(
        partial(pct_change, col=name),
        partial(clean_data, name=name),
        download_market
    )

def get_all_merged_data_norm(assets_config, start, end):
    """
    (PL) Pobiera wiele aktywów i łączy je w jedną tabelę na podstawie indeksu dat.
    (EN) Fetches multiple assets and merges them into a single table based on date index.
    """
    dfs = [
        asset_pipeline_norm(name)((ticker, start, end))
        for ticker, name in assets_config
    ]
    return reduce(
        lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how='inner'),
        dfs
    )


def get_all_data_with_extremes(assets_config, start, end):
    """
    (PL) Pobiera dane, łączy je i oblicza ekstrema (Max/Min) dla każdego aktywa.
    (EN) Fetches data, merges it, and calculates extremes (Max/Min) for each asset.
    """
    dfs = [
        asset_pipeline_norm(name)((ticker, start, end))
        for ticker, name in assets_config
    ]

    merged_df = reduce(
        lambda left, right: pd.merge(
            left, right, left_index=True, right_index=True, how='inner'
        ),
        dfs
    )
    extremes_report = {
        name: ext_pct_change(merged_df, f"{name}_pct_change")
        for _, name in assets_config
    }

    return merged_df, extremes_report

def get_total_change(ticker, name, start, end, decimals=3):
    """
    (PL) Pełny potok: Pobiera -> Czyści -> Oblicza % -> Zaokrągla.
    (EN) Full pipeline: Fetches -> Cleans -> Calculates % -> Rounds.
    """
    pipeline = compose(
        partial(round, ndigits=decimals),
        partial(total_change, col=name),
        partial(clean_data, name=name),
        download_market
    )

    return pipeline((ticker, start, end))


def get_regression_analysis_report(assets_config, start, end, x_asset_name, y_asset_name):
    """
    (PL) Pełny proces: Pobiera dane dla wielu aktywów, łączy je i zwraca model regresji.
    (EN) Full process: Fetches data for multiple assets, merges them, and returns the regression model.
    """
    dfs = [
        asset_pipeline_norm(name)((ticker, start, end))
        for ticker, name in assets_config
    ]

    merged_df = reduce(
        lambda left, right: pd.merge(
            left, right, left_index=True, right_index=True, how='inner'
        ),
        dfs
    )
    x_col = f"{x_asset_name}_pct_change"
    y_col = f"{y_asset_name}_pct_change"

    return lin_reg(merged_df, x_col, y_col)


def get_roi_report(df, asset_name, amount):
    """
    (PL) Generuje kompletny raport ROI dla konkretnego aktywa.
    (EN) Generates a complete ROI report for a specific asset.
    """
    col_name = f"{asset_name}_pct_change"
    roi_series = roi_calc(df[col_name], amount)

    final_value = roi_series.iloc[-1]
    profit = final_value - amount
    profit_pct = (profit / amount) * 100
    icon = "🚀" if profit_pct > 0 else "📉"

    return final_value, profit, profit_pct, icon