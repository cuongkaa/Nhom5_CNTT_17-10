# run_papermill.py
import os
import papermill as pm
from datetime import datetime
from pathlib import Path

# Lấy đường dẫn gốc tuyệt đối của dự án (nơi chứa file run_papermill.py này)
PROJECT_ROOT = Path(__file__).parent.resolve()

# Định nghĩa các đường dẫn chuẩn xác
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "PRSA2017_Data_20130301-20170228.zip"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
RUNS_DIR = NOTEBOOKS_DIR / "runs"

# Tạo thư mục output
os.makedirs(RUNS_DIR, exist_ok=True)
os.makedirs(DATA_PROCESSED, exist_ok=True)

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
KERNEL = "python3"

print(f"🚀 STARTING PIPELINE từ: {PROJECT_ROOT} 🚀\n")

# Hàm chạy notebook chung để code gọn hơn
def run_nb(input_name, output_name, params):
    input_path = NOTEBOOKS_DIR / input_name
    output_path = RUNS_DIR / output_name
    
    print(f"--- Running {input_name} ---")
    try:
        pm.execute_notebook(
            str(input_path),
            str(output_path),
            parameters=params,
            language="python",
            kernel_name=KERNEL,
            progress_bar=True,
            cwd=str(NOTEBOOKS_DIR) # QUAN TRỌNG: Ép notebook chạy tại thư mục notebooks/
        )
        print(f"✅ Success.\n")
    except Exception as e:
        print(f"❌ Failed: {e}")
        exit(1)

# --------------------------------------------------------------------------
# 1. Preprocessing
# --------------------------------------------------------------------------
run_nb(
    "preprocessing_and_eda.ipynb",
    f"1_preprocessing_eda_{ts}.ipynb",
    dict(
        USE_UCIMLREPO=False,
        # Truyền đường dẫn tuyệt đối (String) để notebook không bị lạc
        RAW_ZIP_PATH=str(DATA_RAW),
        OUTPUT_CLEANED_PATH=str(DATA_PROCESSED / "cleaned.parquet"),
        LAG_HOURS=[1, 3, 24],
    )
)

# --------------------------------------------------------------------------
# 2. Regression
# --------------------------------------------------------------------------
run_nb(
    "regression_modelling.ipynb",
    f"2_regression_{ts}.ipynb",
    dict(
        USE_UCIMLREPO=False,
        RAW_ZIP_PATH=str(DATA_RAW),
        LAG_HOURS=[1, 3, 24],
        HORIZON=1,
        TARGET_COL="PM2.5",
        OUTPUT_REG_DATASET_PATH=str(DATA_PROCESSED / "dataset_for_regression.parquet"),
        CUTOFF="2017-01-01",
        MODEL_OUT="regressor.joblib",
        METRICS_OUT="regression_metrics.json",
        PRED_SAMPLE_OUT="regression_predictions_sample.csv",
    )
)

# --------------------------------------------------------------------------
# 3. ARIMA
# --------------------------------------------------------------------------
run_nb(
    "arima_forecasting.ipynb",
    f"3_arima_{ts}.ipynb",
    dict(
        RAW_ZIP_PATH=str(DATA_RAW),
        STATION="Aotizhongxin",
        VALUE_COL="PM2.5",
        CUTOFF="2017-01-01",
        P_MAX=3, Q_MAX=3, D_MAX=2, IC="aic",
        ARTIFACTS_PREFIX="arima_pm25",
    )
)

print("🎉 PIPELINE FINISHED! 🎉")