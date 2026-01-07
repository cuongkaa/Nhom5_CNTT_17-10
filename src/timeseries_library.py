# src/timeseries_library.py
from __future__ import annotations

import json
import warnings
import numpy as np
import pandas as pd
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List

from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Xử lý import đường dẫn
try:
    from src.classification_library import (
        Paths,
        _ensure_dirs,
        load_beijing_air_quality,
        clean_air_quality_df,
    )
except ImportError:
    from classification_library import (
        Paths,
        _ensure_dirs,
        load_beijing_air_quality,
        clean_air_quality_df,
    )

warnings.filterwarnings("ignore")

# -------------------------------------------------------------------------
# 1. DATA PREPARATION
# -------------------------------------------------------------------------
@dataclass(frozen=True)
class StationSeriesConfig:
    station: str
    target_col: str = "PM2.5"
    exog_cols: tuple[str, ...] = () 
    freq: str = "H"
    fill_method: str = "interpolate_time"
    clip_negative: bool = True

def prepare_station_data(
    df: pd.DataFrame, 
    cfg: StationSeriesConfig
) -> Tuple[pd.Series, Optional[pd.DataFrame]]:
    # Validate
    cols_needed = {"datetime", "station", cfg.target_col}
    if not cols_needed.issubset(df.columns):
        raise ValueError(f"Thiếu cột: {cols_needed - set(df.columns)}")

    # Lọc trạm và sort
    sdf = df[df["station"] == cfg.station].copy()
    sdf = sdf.sort_values("datetime")
    sdf.set_index("datetime", inplace=True)

    # Resample index
    full_idx = pd.date_range(start=sdf.index.min(), end=sdf.index.max(), freq=cfg.freq)
    sdf = sdf.reindex(full_idx)

    y = pd.to_numeric(sdf[cfg.target_col], errors="coerce")
    
    X = None
    if cfg.exog_cols:
        X = sdf[list(cfg.exog_cols)].apply(pd.to_numeric, errors="coerce")

    if cfg.fill_method == "interpolate_time":
        y = y.interpolate(method="time", limit_direction="both")
        if X is not None:
            X = X.interpolate(method="time", limit_direction="both")
    elif cfg.fill_method == "ffill":
        y = y.ffill().bfill()
        if X is not None:
            X = X.ffill().bfill()

    if cfg.clip_negative:
        y = y.where(y >= 0, 0.0)

    return y, X

# -------------------------------------------------------------------------
# 2. DIAGNOSTICS & HELPERS
# -------------------------------------------------------------------------
def choose_d_by_adf(s: pd.Series, max_d: int = 2, alpha: float = 0.05) -> int:
    x = s.dropna()
    for d in range(max_d + 1):
        if len(x) < 50: break
        try:
            p_val = adfuller(x, autolag="AIC")[1]
            if p_val < alpha:
                return d
        except:
            break
        x = x.diff().dropna()
    return max_d

def describe_time_series(s: pd.Series, seasonal_periods=(24, 168)) -> dict:
    s_clean = s.dropna()
    stats = {
        "n_obs": len(s_clean),
        "mean": float(s_clean.mean()),
        "std": float(s_clean.std()),
    }
    adf_p = None
    if len(s_clean) > 50:
        try:
            adf_p = float(adfuller(s_clean, autolag="AIC")[1])
        except: pass
            
    ac_metrics = {}
    for lag in seasonal_periods:
        if len(s_clean) > lag + 10:
            ac_metrics[f"autocorr_lag_{lag}"] = float(s_clean.autocorr(lag=lag))
            
    return {**stats, "adf_pvalue": adf_p, **ac_metrics}

# -------------------------------------------------------------------------
# 3. GRID SEARCH
# -------------------------------------------------------------------------
def grid_search_arima_order(
    s: pd.Series,
    p_max: int = 3,
    d_max: int = 2,
    q_max: int = 3,
    ic: str = "aic",
) -> dict:
    train_data = s.dropna()
    d_suggested = choose_d_by_adf(train_data, max_d=d_max)
    
    d_candidates = [d_suggested]
    p_values = range(p_max + 1)
    q_values = range(q_max + 1)

    best_score = float("inf")
    best_order = (1, 1, 1) # Default fallback

    print(f"Running Grid Search (Max p={p_max}, q={q_max}, d={d_suggested})...")
    
    for p in p_values:
        for d in d_candidates:
            for q in q_values:
                order = (p, d, q)
                try:
                    model = ARIMA(train_data, order=order, enforce_stationarity=False, enforce_invertibility=False)
                    res = model.fit()
                    score = getattr(res, ic)
                    if score < best_score:
                        best_score = score
                        best_order = order
                except:
                    continue

    print(f"Best Order Found: {best_order} with {ic}={best_score}")
    return {"best_order": best_order, "best_score": best_score}

# -------------------------------------------------------------------------
# 4. TRAINING & FORECASTING
# -------------------------------------------------------------------------
def fit_arima_model(
    y_train: pd.Series,
    y_test: pd.Series,
    order: Tuple[int, int, int],
    seasonal_order: Tuple[int, int, int, int] = (0, 0, 0, 0),
    exog_train: Optional[pd.DataFrame] = None,
    exog_test: Optional[pd.DataFrame] = None
) -> dict:
    
    print(f"Fitting ARIMA{order} x {seasonal_order}...")
    
    model = ARIMA(
        endog=y_train, 
        exog=exog_train,
        order=order, 
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    model_fit = model.fit()

    steps = len(y_test)
    fc_res = model_fit.get_forecast(steps=steps, exog=exog_test)
    
    y_pred = fc_res.predicted_mean
    y_pred.index = y_test.index
    conf_int = fc_res.conf_int()

    mask = np.isfinite(y_test) & np.isfinite(y_pred)
    y_t, y_p = y_test[mask], y_pred[mask]
    
    mae = mean_absolute_error(y_t, y_p) if len(y_t) > 0 else None
    
    mse = mean_squared_error(y_t, y_p) if len(y_t) > 0 else 0
    rmse = np.sqrt(mse)
    
    denom = (np.abs(y_t) + np.abs(y_p)) / 2.0
    smape = np.mean(np.abs(y_t - y_p) / denom) * 100 if len(y_t) > 0 else None

    metrics = {
        "MAE": round(mae, 4) if mae else None,
        "RMSE": round(rmse, 4) if rmse else None,
        "sMAPE": round(smape, 4) if smape else None,
        "AIC": round(model_fit.aic, 4)
    }

    return {
        "model": model_fit,
        "forecast": y_pred,
        "conf_int": conf_int,
        "metrics": metrics
    }

# -------------------------------------------------------------------------
# 5. WORKFLOW ORCHESTRATOR
# -------------------------------------------------------------------------
def forecast_workflow(
    paths: Paths,
    station: str = "Aotizhongxin",
    cutoff: str = "2017-01-01",
    p_max: int = 3,
    q_max: int = 3,
    d_max: int = 2,
    ic: str = "aic",
    target_col: str = "PM2.5",
    exog_cols: Optional[List[str]] = None,
    seasonal_order: Tuple[int, int, int, int] = (0, 0, 0, 0),
    artifacts_prefix: str = "arima_pm25"
) -> dict:
    
    _ensure_dirs(paths.data_processed)
    
    # 1. Load Data
    raw_zip = paths.data_raw / "PRSA2017_Data_20130301-20170228.zip"
    
    # --- ĐÃ SỬA LỖI Ở ĐÂY: Xóa bỏ use_ucimlrepo=False ---
    df = load_beijing_air_quality(raw_zip_path=raw_zip)
    # ----------------------------------------------------
    
    df = clean_air_quality_df(df)

    # 2. Prepare Data
    print(f"Preparing data for station: {station}")
    exog_tuple = tuple(exog_cols) if exog_cols else ()
    cfg = StationSeriesConfig(station=station, target_col=target_col, exog_cols=exog_tuple)
    y, X = prepare_station_data(df, cfg)
    
    # 3. Split
    cutoff_ts = pd.Timestamp(cutoff)
    train_mask = y.index < cutoff_ts
    test_mask = y.index >= cutoff_ts
    y_train, y_test = y[train_mask], y[test_mask]
    
    X_train, X_test = None, None
    if X is not None:
        X_train, X_test = X.loc[train_mask], X.loc[test_mask]

    print(f"Train samples: {len(y_train)}, Test samples: {len(y_test)}")

    # 4. Grid Search
    final_order = (1, 1, 1)
    
    if seasonal_order == (0, 0, 0, 0) and X is None:
        gs_res = grid_search_arima_order(y_train, p_max=p_max, q_max=q_max, d_max=d_max, ic=ic)
        final_order = gs_res["best_order"]
    else:
        print("Skipping Grid Search for Advanced Models")

    # 5. Fit & Forecast
    res = fit_arima_model(
        y_train, y_test, 
        order=final_order, 
        seasonal_order=seasonal_order, 
        exog_train=X_train, 
        exog_test=X_test
    )
    
    # 6. Save
    summary = {
        "station": station,
        "cutoff": cutoff,
        "best_order": final_order,
        "metrics": res["metrics"],
        "diagnostics": describe_time_series(y)
    }
    
    pred_df = pd.DataFrame({
        "datetime": y_test.index,
        "y_true": y_test.values,
        "y_pred": res["forecast"].values,
        "lower_ci": res["conf_int"].iloc[:, 0].values,
        "upper_ci": res["conf_int"].iloc[:, 1].values
    })
    
    pred_df.to_csv(paths.data_processed / f"{artifacts_prefix}_predictions.csv", index=False)
    with open(paths.data_processed / f"{artifacts_prefix}_summary.json", "w") as f:
        json.dump(summary, f, indent=4)

    print(f"--- [DONE] RMSE: {res['metrics']['RMSE']} ---")
    return {"summary": summary, "predictions": pred_df}