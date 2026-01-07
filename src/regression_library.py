# src/regression_library.py
from __future__ import annotations

import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import HistGradientBoostingRegressor

# Import các hàm từ classification_library để tái sử dụng
try:
    from src.classification_library import (
        Paths,
        _ensure_dirs,
        load_beijing_air_quality,
        clean_air_quality_df,
        add_time_features,
        add_lag_features
    )
except ImportError:
    from classification_library import (
        Paths,
        _ensure_dirs,
        load_beijing_air_quality,
        clean_air_quality_df,
        add_time_features,
        add_lag_features
    )

# -------------------------------------------------------------------------
# 1. DATA PREPARATION FOR REGRESSION
# -------------------------------------------------------------------------
def make_regression_target(
    df: pd.DataFrame,
    target_col: str = "PM2.5",
    horizon: int = 1,
    out_col: str = "target"
) -> pd.DataFrame:
    """
    Tạo biến mục tiêu (Label) cho bài toán hồi quy.
    y(t) = PM2.5 tại thời điểm (t + horizon).
    """
    df = df.copy()
    
    if "station" in df.columns:
        df = df.sort_values(["station", "datetime"])
        # Shift lùi về sau để lấy giá trị tương lai
        df[out_col] = df.groupby("station")[target_col].shift(-horizon)
    else:
        df = df.sort_values(["datetime"])
        df[out_col] = df[target_col].shift(-horizon)

    df = df.dropna(subset=[out_col])
    return df

def run_prepare_regression_dataset(
    paths: Paths,
    raw_zip_path: str,
    lag_hours: list[int] = [1, 3, 24],
    horizon: int = 1
) -> None:
    print("--- [Regression] Preparing Dataset ---")
    
    df = load_beijing_air_quality(raw_zip_path)
    df = clean_air_quality_df(df)
    df = add_time_features(df)
    
    print(f"Adding lag features: {lag_hours}")
    df = add_lag_features(df, lag_hours=lag_hours, target_col="PM2.5")
    
    weather_cols = ["TEMP", "PRES", "DEWP", "RAIN", "WSPM"]
    for col in weather_cols:
        if col in df.columns:
            df = add_lag_features(df, lag_hours=[1], target_col=col)

    print(f"Creating target with horizon = {horizon} hour(s)")
    df = make_regression_target(df, target_col="PM2.5", horizon=horizon, out_col="y")

    out_path = paths.data_processed / "dataset_for_regression.parquet"
    print(f"Saving to: {out_path}")
    df.to_parquet(out_path, index=False)
    print(f"--- [DONE] Shape: {df.shape} ---")


# -------------------------------------------------------------------------
# 2. MODEL TRAINING & EVALUATION
# -------------------------------------------------------------------------
def time_split(df: pd.DataFrame, cutoff: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff_ts = pd.Timestamp(cutoff)
    train = df[df["datetime"] < cutoff_ts].copy()
    test = df[df["datetime"] >= cutoff_ts].copy()
    return train, test

def train_regressor(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_col: str = "y"
) -> dict:
    """
    Huấn luyện mô hình HistGradientBoostingRegressor.
    """
    drop_cols = ["datetime", target_col]
    features = [c for c in train_df.columns if c not in drop_cols]
    
    X_train = train_df[features]
    y_train = train_df[target_col]
    X_test = test_df[features]
    y_test = test_df[target_col]

    # Preprocessing
    cat_cols = X_train.select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = X_train.select_dtypes(exclude=["object", "category"]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", num_cols),
            ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cat_cols),
        ],
        verbose_feature_names_out=False
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", HistGradientBoostingRegressor(random_state=42, max_iter=200))
    ])

    print(f"Training on {X_train.shape} samples...")
    model.fit(X_train, y_train)

    print("Predicting on Test set...")
    y_pred = model.predict(X_test)

    # Metrics
    mae = mean_absolute_error(y_test, y_pred)
    
    # --- SỬA LỖI TẠI ĐÂY: Tính MSE rồi lấy căn bậc 2 ---
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse) 
    # ---------------------------------------------------
    
    r2 = r2_score(y_test, y_pred)

    metrics = {
        "MAE": round(mae, 4),
        "RMSE": round(rmse, 4),
        "R2": round(r2, 4),
        "n_train": len(X_train),
        "n_test": len(X_test)
    }

    results_df = test_df[["datetime", "station"]].copy() if "station" in test_df.columns else test_df[["datetime"]].copy()
    results_df["Actual"] = y_test.values
    results_df["Forecast"] = y_pred
    
    return {
        "model": model,
        "metrics": metrics,
        "results_df": results_df
    }

def run_training_pipeline(
    paths: Paths,
    cutoff: str = "2017-01-01"
) -> None:
    input_path = paths.data_processed / "dataset_for_regression.parquet"
    if not input_path.exists():
        raise FileNotFoundError("Dataset not found. Run preparation first.")

    df = pd.read_parquet(input_path)
    
    train_df, test_df = time_split(df, cutoff)
    print(f"Train size: {len(train_df)} | Test size: {len(test_df)}")
    
    result = train_regressor(train_df, test_df)
    
    print("Saving artifacts...")
    metrics_path = paths.data_processed / "regression_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(result["metrics"], f, indent=4)
        
    model_path = paths.data_processed / "regressor.joblib"
    joblib.dump(result["model"], model_path)
    
    pred_path = paths.data_processed / "regression_predictions.csv"
    result["results_df"].to_csv(pred_path, index=False)
    
    print(f"--- [DONE] RMSE: {result['metrics']['RMSE']} ---")