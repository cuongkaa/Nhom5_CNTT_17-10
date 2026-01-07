# src/classification_library.py
from __future__ import annotations

import zipfile
import ast
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass

# -------------------------------------------------------------------------
# CẤU HÌNH PATHS (Hỗ trợ quản lý đường dẫn OOP)
# -------------------------------------------------------------------------
@dataclass(frozen=True)
class Paths:
    project_root: Path

    @property
    def data_raw(self) -> Path:
        return self.project_root / "data" / "raw"

    @property
    def data_processed(self) -> Path:
        return self.project_root / "data" / "processed"

def _ensure_dirs(*dirs: Path) -> None:
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# 1. DATA LOADING (Tải và gộp dữ liệu từ ZIP)
# -------------------------------------------------------------------------
def load_beijing_air_quality(
    raw_zip_path: str | Path,
) -> pd.DataFrame:
    """
    Đọc file ZIP chứa 12 file CSV của các trạm và gộp thành 1 DataFrame.
    """
    raw_zip_path = Path(raw_zip_path)
    if not raw_zip_path.exists():
        raise FileNotFoundError(f"ZIP file not found at: {raw_zip_path}")

    dfs: list[pd.DataFrame] = []
    with zipfile.ZipFile(raw_zip_path, "r") as zf:
        # Lọc các file .csv trong zip
        csv_files = [m for m in zf.namelist() if m.lower().endswith(".csv")]
        
        if not csv_files:
            raise ValueError("No CSV files found inside the ZIP archive.")

        print(f"Loading {len(csv_files)} station files from zip...")
        for csv_file in csv_files:
            with zf.open(csv_file) as f:
                # Đọc csv, đảm bảo các biến khí tượng là số
                df_station = pd.read_csv(f)
                dfs.append(df_station)

    # Gộp tất cả các trạm lại
    df_combined = pd.concat(dfs, ignore_index=True)
    return df_combined

# -------------------------------------------------------------------------
# 2. DATA CLEANING & NORMALIZATION (Làm sạch & Chuẩn hóa thời gian)
# -------------------------------------------------------------------------
def clean_air_quality_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Thực hiện:
    1. Xử lý tên cột (strip space).
    2. Xử lý giá trị NA/Null.
    3. Tạo cột datetime chuẩn.
    4. Ép kiểu dữ liệu số (numeric coercion).
    5. Sắp xếp theo Station và Time (QUAN TRỌNG cho Time Series).
    """
    df = df.copy()
    
    # 1. Chuẩn hóa tên cột
    df.columns = [c.strip() for c in df.columns]

    # 2. Xử lý các ký tự đại diện cho NA
    df = df.replace(["NA", "N/A", "na", "null", "None", ""], np.nan)

    # 3. Tạo cột datetime
    # Lab yêu cầu dự báo theo giờ, nên cần đầy đủ year, month, day, hour
    required_time_cols = {"year", "month", "day", "hour"}
    if required_time_cols.issubset(set(df.columns)):
        df["datetime"] = pd.to_datetime(
            df[["year", "month", "day", "hour"]],
            errors="coerce"
        )
    elif "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    else:
        raise ValueError("Dataset missing required time columns (year, month, day, hour).")

    # 4. Ép kiểu số cho các biến quan trắc
    numeric_cols = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", 
                    "TEMP", "PRES", "DEWP", "RAIN", "WSPM"]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5. Sắp xếp dữ liệu
    # Bắt buộc phải sort theo Station -> Time để tính Lag không bị sai
    if "station" in df.columns:
        df = df.sort_values(by=["station", "datetime"]).reset_index(drop=True)
    else:
        df = df.sort_values(by=["datetime"]).reset_index(drop=True)

    return df

# -------------------------------------------------------------------------
# 3. FEATURE ENGINEERING (Tạo đặc trưng cho Hồi quy & Time Series)
# -------------------------------------------------------------------------
def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Thêm các đặc trưng thời gian để mô hình hồi quy học được tính chu kỳ (seasonality).
    """
    df = df.copy()
    dt = df["datetime"]

    # Month (1-12): Tính mùa vụ theo năm
    df["month"] = dt.dt.month.astype("int8")
    
    # Day of Week (0=Mon, 6=Sun): Tính chu kỳ tuần
    df["dow"] = dt.dt.dayofweek.astype("int8")
    
    # Hour (0-23): Tính chu kỳ ngày
    df["hour"] = dt.dt.hour.astype("int8")

    # Cyclical Features (Quan trọng cho Linear Regression/Neural Net)
    # Giúp mô hình hiểu 23h gần với 0h
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24.0)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24.0)
    
    return df

def _coerce_lag_hours(lag_hours) -> tuple[int, ...]:
    """Helper xử lý input lag_hours từ Papermill (có thể bị convert thành string)."""
    if lag_hours is None:
        return tuple()
    
    if isinstance(lag_hours, str):
        try:
            # Thử parse literal (ví dụ string "[1, 3, 24]")
            val = ast.literal_eval(lag_hours)
            if isinstance(val, int): return (val,)
            return tuple(val)
        except:
            return tuple()
            
    if isinstance(lag_hours, int):
        return (lag_hours,)
        
    return tuple(lag_hours)

def add_lag_features(
    df: pd.DataFrame,
    lag_hours: tuple[int, ...] | list[int] | str = (1, 3, 24),
    target_col: str = "PM2.5"
) -> pd.DataFrame:
    """
    Tạo các biến trễ (Lag features).
    Ví dụ: PM2.5_lag1 nghĩa là giá trị PM2.5 của 1 giờ trước.
    Đây là đặc trưng quan trọng nhất cho Baseline Regression.
    """
    df = df.copy()
    lags = _coerce_lag_hours(lag_hours)
    
    if not lags:
        return df

    # Nếu có cột station, phải group theo station trước khi shift
    # Nếu không, giá trị của trạm này sẽ trượt sang trạm kia -> SAI (Data Leakage)
    if "station" in df.columns:
        grouper = df.groupby("station")[target_col]
        for lag in lags:
            df[f"{target_col}_lag{lag}"] = grouper.shift(lag)
    else:
        for lag in lags:
            df[f"{target_col}_lag{lag}"] = df[target_col].shift(lag)

    return df

# -------------------------------------------------------------------------
# 4. PIPELINE ORCHESTRATOR (Hàm gọi chính cho Papermill)
# -------------------------------------------------------------------------
def run_processing_pipeline(
    raw_zip_path: str,
    processed_output_path: str,
    lag_hours: list[int] = [1, 3, 24]
) -> None:
    """
    Hàm này sẽ được gọi từ Notebook 'preprocessing_and_eda.ipynb'.
    Nó thực thi toàn bộ quy trình từ Raw -> Processed.
    """
    print("--- [START] Processing Pipeline ---")
    
    # 1. Load
    print(f"Loading data from: {raw_zip_path}")
    df = load_beijing_air_quality(raw_zip_path)
    
    # 2. Clean
    print("Cleaning data & Parsing datetime...")
    df = clean_air_quality_df(df)
    
    # 3. Feature Engineering
    print("Adding time features...")
    df = add_time_features(df)
    
    print(f"Adding lag features for PM2.5: {lag_hours}")
    df = add_lag_features(df, lag_hours=lag_hours, target_col="PM2.5")

    # 4. Save
    out_path = Path(processed_output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving processed data to: {out_path}")
    df.to_parquet(out_path, index=False)
    
    print(f"--- [DONE] Shape: {df.shape} ---")