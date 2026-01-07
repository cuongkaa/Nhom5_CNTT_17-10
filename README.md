# Air Quality Timeseries - Dự Án Phân Tích và Dự Báo Chất Lượng Không Khí

## 📋 Giới Thiệu

Dự án này tập trung vào việc phân tích dữ liệu chuỗi thời gian (timeseries) chất lượng không khí tại Bắc Kinh, kéo dài từ **01/03/2013 đến 28/02/2017**. Dự án sử dụng ba phương pháp chính để dự báo nồng độ **PM2.5**:

1. **Hồi quy (Regression)** - Sử dụng HistGradientBoostingRegressor
2. **Dự báo ARIMA** - Sử dụng mô hình ARIMA thích ứng cho từng trạm
3. **Phân loại (Classification)** - Phân loại mức độ ô nhiễm không khí

---

## 🏗️ Cấu Trúc Dự Án

```
air_quality_timeseries/
├── README.md                      # Tài liệu hướng dẫn dự án
├── LICENSE.txt                    # Giấy phép sử dụng
├── requirements.txt               # Danh sách các thư viện cần thiết
├── run_papermill.py              # Script chạy toàn bộ pipeline
│
├── data/
│   ├── raw/                       # Dữ liệu thô (chưa xử lý)
│   │   └── PRSA2017_Data_20130301-20170228.zip  # File ZIP dữ liệu gốc
│   └── processed/                 # Dữ liệu đã xử lý
│       ├── cleaned.parquet        # Dữ liệu sau khi làm sạch
│       ├── dataset_for_regression.parquet  # Dữ liệu cho mô hình hồi quy
│       ├── regressor.joblib       # Mô hình hồi quy đã huấn luyện
│       ├── regression_metrics.json # Các chỉ số đánh giá hồi quy
│       ├── regression_predictions.csv # Dự báo đầy đủ từ hồi quy
│       ├── regression_predictions_sample.csv # Mẫu dự báo hồi quy
│       ├── arima_pm25_predictions.csv # Dự báo từ mô hình ARIMA
│       └── arima_pm25_summary.json    # Thông tin tóm tắt ARIMA
│
├── notebooks/                     # Các Jupyter Notebook
│   ├── preprocessing_and_eda.ipynb      # Xử lý dữ liệu & Phân tích khám phá
│   ├── regression_modelling.ipynb       # Huấn luyện mô hình hồi quy
│   ├── arima_forecasting.ipynb          # Xây dựng mô hình ARIMA
│   └── runs/                            # Kết quả chạy notebook được tạo tự động
│       ├── 1_preprocessing_eda_20260107_062928.ipynb
│       ├── 2_regression_20260107_062928.ipynb
│       ├── 3_arima_20260107_062928.ipynb
│       └── ...
│
└── src/                           # Thư viện Python (módules)
    ├── __init__.py               # Khởi tạo package
    ├── classification_library.py # Các hàm dùng chung (tải dữ liệu, làm sạch, tạo features)
    ├── regression_library.py     # Các hàm cho mô hình hồi quy
    ├── timeseries_library.py     # Các hàm cho mô hình ARIMA
    └── __pycache__/              # Cache Python (tự động tạo)
```

---

## 🔧 Yêu Cầu Hệ Thống

### Python và Thư Viện

- **Python**: >= 3.8
- **Thư viện chính**:
  - `pandas>=2.0` - Xử lý và phân tích dữ liệu
  - `numpy>=1.24` - Tính toán số học
  - `scikit-learn>=1.3` - Machine Learning
  - `statsmodels>=0.14` - Mô hình thống kê (ARIMA, kiểm định)
  - `matplotlib>=3.7` - Vẽ biểu đồ
  - `joblib>=1.3` - Lưu/tải mô hình
  - `papermill>=2.5` - Chạy notebook với tham số
  - `pyarrow>=14.0` - Xử lý file Parquet
  - `ucimlrepo>=0.0.7` - Tải dữ liệu từ UCI Machine Learning Repository
  - `nbformat>=5.9` - Xử lý định dạng Notebook

---

## 📦 Cài Đặt

### 1. Sao Chép Dự Án
```bash
git clone <repository-url>
cd air_quality_timeseries
```

### 2. Tạo Môi Trường Ảo (Virtual Environment)
```bash
# Với venv
python -m venv venv
source venv/bin/activate      # Trên Linux/MacOS
venv\Scripts\activate          # Trên Windows PowerShell
```

### 3. Cài Đặt Các Thư Viện
```bash
pip install -r requirements.txt
```

---

## 🚀 Hướng Dẫn Sử Dụng

### Cách 1: Chạy Toàn Bộ Pipeline (Tự Động)

Sử dụng script `run_papermill.py` để chạy tất cả các notebook theo thứ tự:

```bash
python run_papermill.py
```

**Quy trình thực thi:**
1. **Preprocessing & EDA** - Làm sạch dữ liệu, thêm lag features, phân tích khám phá
2. **Regression Modelling** - Huấn luyện HistGradientBoostingRegressor
3. **ARIMA Forecasting** - Xây dựng mô hình ARIMA tối ưu và dự báo

**Kết quả:**
- Các notebook được lưu trong `notebooks/runs/` với timestamp
- Các artifacts (mô hình, dự báo, metrics) được lưu trong `data/processed/`

### Cách 2: Chạy Từng Notebook Riêng Lẻ

Mở Jupyter Notebook và chạy từng cell:

```bash
jupyter notebook notebooks/
```

Sau đó, mở các file lần lượt:
- `notebooks/preprocessing_and_eda.ipynb` - Khám phá và làm sạch dữ liệu
- `notebooks/regression_modelling.ipynb` - Huấn luyện mô hình hồi quy
- `notebooks/arima_forecasting.ipynb` - Dự báo với ARIMA

---

## 📊 Chi Tiết Các Notebook

### 1. **preprocessing_and_eda.ipynb** - Xử Lý Dữ Liệu & Phân Tích Khám Phá

**Mục đích:**
- Tải dữ liệu từ file ZIP hoặc UCI repository
- Làm sạch dữ liệu (xử lý giá trị thiếu, ngoài phạm vi)
- Thêm các feature theo thời gian (giờ, ngày, tháng, v.v.)
- Thêm lag features (PM2.5 tại t-1, t-3, t-24)
- Phân tích khám phá dữ liệu (EDA) - thống kê, biểu đồ

**Đầu vào:**
- `USE_UCIMLREPO` (bool): Tải từ UCI repo hay file ZIP cục bộ
- `RAW_ZIP_PATH` (str): Đường dẫn file ZIP (nếu không dùng UCI repo)
- `OUTPUT_CLEANED_PATH` (str): Đường dẫn lưu dữ liệu đã làm sạch

**Đầu ra:**
- File Parquet chứa dữ liệu đã làm sạch và có features
- Biểu đồ thống kê chất lượng không khí

---

### 2. **regression_modelling.ipynb** - Mô Hình Hồi Quy

**Mục đích:**
- Tạo dataset cho bài toán hồi quy (X, y)
- Chia dữ liệu thành train/test
- Huấn luyện mô hình **HistGradientBoostingRegressor**
- Đánh giá mô hình (MAE, RMSE, R²)
- Lưu mô hình và dự báo

**Tham số chính:**
- `HORIZON` (int): Dự báo h bước thời gian phía trước (thường là 1)
- `TARGET_COL` (str): Cột mục tiêu (mặc định "PM2.5")
- `LAG_HOURS` (list): Danh sách các lag để tạo features (ví dụ: [1, 3, 24])
- `CUTOFF` (str): Ngày cắt train/test (ví dụ: "2017-01-01")

**Đầu ra:**
- `regressor.joblib` - Mô hình đã huấn luyện
- `regression_metrics.json` - Các chỉ số MAE, RMSE, R²
- `regression_predictions_sample.csv` - Mẫu dự báo (1000 dòng)
- `regression_predictions.csv` - Dự báo đầy đủ

---

### 3. **arima_forecasting.ipynb** - Mô Hình ARIMA

**Mục đích:**
- Chuẩn bị dữ liệu chuỗi thời gian cho một trạm cụ thể
- Kiểm tra tính dừng (stationarity) bằng ADF test
- Tìm kiếm tham số tối ưu (p, d, q) bằng Grid Search
- Huấn luyện mô hình ARIMA tối ưu
- Dự báo PM2.5 trong tương lai

**Tham số chính:**
- `STATION` (str): Trạm khí tượng (ví dụ: "Aotizhongxin")
- `VALUE_COL` (str): Cột cần dự báo (mặc định "PM2.5")
- `CUTOFF` (str): Ngày bắt đầu dữ liệu kiểm tra
- `P_MAX, Q_MAX, D_MAX` (int): Giới hạn tìm kiếm các tham số
- `IC` (str): Tiêu chí chọn mô hình ("aic" hoặc "bic")

**Đầu ra:**
- `arima_pm25_predictions.csv` - Dự báo PM2.5
- `arima_pm25_summary.json` - Thông tin mô hình ARIMA tối ưu

---

## 🛠️ Các Hàm Chính trong Thư Viện

### **classification_library.py** (Các hàm dùng chung)

| Hàm | Mục Đích |
|-----|---------|
| `Paths` | Dataclass quản lý đường dẫn dự án |
| `load_beijing_air_quality()` | Tải dữ liệu từ UCI repo hoặc file ZIP |
| `clean_air_quality_df()` | Làm sạch dữ liệu (xử lý NaN, ngoài phạm vi) |
| `add_time_features()` | Thêm feature theo thời gian (giờ, ngày, tháng) |
| `add_lag_features()` | Thêm lag features (PM2.5 tại t-1, t-3, v.v.) |
| `_ensure_dirs()` | Tạo thư mục nếu chưa tồn tại |

### **regression_library.py** (Hồi quy)

| Hàm | Mục Đích |
|-----|---------|
| `make_regression_target()` | Tạo biến mục tiêu cho hồi quy |
| `make_regression_dataset()` | Tạo dataset X, y cho hồi quy |
| `train_regression_model()` | Huấn luyện và đánh giá mô hình |
| `make_predictions()` | Dự báo sử dụng mô hình |

### **timeseries_library.py** (ARIMA)

| Hàm | Mục Đích |
|-----|---------|
| `StationSeriesConfig` | Cấu hình cho chuỗi thời gian |
| `prepare_station_data()` | Chuẩn bị dữ liệu chuỗi thời gian |
| `check_stationarity()` | Kiểm định tính dừng (ADF, KPSS) |
| `find_optimal_arima()` | Tìm tham số p, d, q tối ưu |
| `forecast_arima()` | Dự báo sử dụng ARIMA |

---

## 📈 Kết Quả Dự Kiến

Sau khi chạy toàn bộ pipeline, bạn sẽ nhận được:

### **1. Mô Hình Hồi Quy**
- MAE, RMSE, R² score
- Dự báo PM2.5 cho tập test
- Phân tích tầm quan trọng của feature

### **2. Mô Hình ARIMA**
- Tham số tối ưu (p, d, q) cho từng trạm
- Dự báo PM2.5 trong tương lai
- Khoảng tin cậy 95% cho dự báo

### **3. Phân Tích Khám Phá (EDA)**
- Thống kê mô tả (mean, std, min, max)
- Biểu đồ phân bố PM2.5
- Mối tương quan giữa các biến
- Xu hướng theo mùa

---

## 🔍 Khắc Phục Sự Cố

### **Lỗi: "No module named 'src'"**
Đảm bảo bạn đang ở thư mục gốc dự án khi chạy:
```bash
cd path/to/air_quality_timeseries
python run_papermill.py
```

### **Lỗi: "File not found: PRSA2017_Data*.zip"**
Tải file dữ liệu từ [UCI ML Repository](https://archive.ics.uci.edu/ml/datasets/beijing+multi-site+air-quality+data) 
và đặt vào thư mục `data/raw/`, hoặc để notebook tự tải từ UCI repo bằng cách set `USE_UCIMLREPO=True`

### **Lỗi: "kernel_name 'python3' not found"**
Kiểm tra tên kernel Jupyter của bạn:
```bash
jupyter kernelspec list
```
Cập nhật `KERNEL` trong `run_papermill.py` nếu cần

### **Notebook chạy chậm**
- Giảm kích thước dữ liệu bằng cách chọn một khoảng thời gian nhỏ hơn
- Giảm số lần lặp Grid Search trong ARIMA (giảm P_MAX, Q_MAX, D_MAX)

---

## 📚 Tài Liệu Tham Khảo

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Scikit-learn Documentation](https://scikit-learn.org/stable/)
- [Statsmodels - ARIMA](https://www.statsmodels.org/stable/tsa.html)
- [Beijing Air Quality Data - UCI ML](https://archive.ics.uci.edu/ml/datasets/beijing+multi-site+air-quality+data)
- [Papermill Documentation](https://papermill.readthedocs.io/)

---

## 📄 Giấy Phép

Dự án này được phân phối theo giấy phép được định nghĩa trong file `LICENSE.txt`.

---

## 👨‍💻 Tác Giả

Xây dựng và duy trì cho các mục đích học tập và nghiên cứu về dự báo chuỗi thời gian.

---

## 📞 Liên Hệ & Hỗ Trợ

Nếu bạn gặp vấn đề hoặc có câu hỏi, vui lòng tạo một issue hoặc liên hệ qua email.

---

**Cập nhật lần cuối:** 07/01/2026
