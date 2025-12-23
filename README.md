# Shopping Cart Analysis & Weighted Association Rules

## 📖 Giới thiệu (Overview)
Dự án này thực hiện phân tích dữ liệu bán lẻ (Market Basket Analysis) để tìm ra các mối quan hệ giữa các sản phẩm thường được mua cùng nhau. 

Điểm đặc biệt của dự án là sự kết hợp giữa **Khai phá luật kết hợp truyền thống** (Apriori/FP-Growth) và **Luật kết hợp có trọng số (Weighted Association Rules)**. Thay vì chỉ đếm tần suất xuất hiện, chúng tôi đánh giá "sức nặng" của từng luật dựa trên **giá trị hóa đơn (Revenue)**, giúp tìm ra những combo sản phẩm mang lại doanh thu cao thực sự (High-value patterns).

---

## 🚀 Tính năng chính (Key Features)

1.  **Xử lý dữ liệu toàn diện**:
    * Làm sạch dữ liệu giao dịch bán lẻ (Retail Data Cleaning).
    * Xử lý các hóa đơn lỗi, lọc dữ liệu theo quốc gia (UK).
    * Tạo ma trận giỏ hàng (Basket Matrix).

2.  **Thuật toán Khai phá (Mining Algorithms)**:
    * **Apriori**: Tìm tập phổ biến và sinh luật kết hợp cơ bản.
    * **FP-Growth**: Tối ưu hóa tốc độ xử lý cho tập dữ liệu lớn.

3.  **Phân tích Trọng số (Topic 3: Weighted Analysis)**:
    * Tính toán **Trọng số hóa đơn (Invoice Weight)** dựa trên tổng tiền.
    * Tính chỉ số **Weighted Support**: Đánh giá tầm quan trọng của luật dựa trên doanh thu.
    * Phân loại chiến lược: *Stars* (Bán chạy & Doanh thu cao), *Niche* (Hiếm & Giá trị cao).

4.  **Trực quan hóa (Visualization)**:
    * Biểu đồ Scatter (Support vs Confidence vs Lift).
    * Biểu đồ mạng lưới (Network Graph) các sản phẩm.
    * Biểu đồ tương tác với Plotly.

5.  **Tự động hóa (Automation)**:
    * Sử dụng **Papermill** để chạy toàn bộ pipeline notebook tự động.

---

## 📂 Cấu trúc dự án (Project Structure)

```text
shopping_cart_analysis/
├── data/
│   ├── raw/
│   │   └── online_retail.csv           # Dữ liệu gốc (Input)
│   └── processed/
│       ├── cleaned_uk_data.csv         # Dữ liệu sau làm sạch
│       ├── basket_bool.parquet         # Ma trận giỏ hàng (đã mã hóa)
│       └── rules_apriori_filtered.csv  # Kết quả luật sau khi lọc
│
├── notebooks/
│   ├── preprocessing_and_eda.ipynb     # Bước 1: EDA & Tiền xử lý
│   ├── basket_preparation.ipynb        # Bước 2: Chuẩn bị Basket Matrix
│   ├── apriori_modelling.ipynb         # Bước 3: Chạy mô hình Apriori & Visualization
│   ├── topic3_weighted_analysis.ipynb  # [MỚI] Bước 4: Phân tích luật có trọng số
│   └── runs/                           # Thư mục chứa kết quả chạy tự động (Papermill)
│
├── src/
│   ├── apriori_library.py              # Thư viện core (DataCleaner, Miner, Visualizer)
│   └── __init__.py
│
├── run_papermill.py                    # Script điều phối chạy toàn bộ pipeline
├── requirements.txt                    # Danh sách thư viện cần thiết
└── README.md                           # Tài liệu dự án

##🛠️ Cài đặt & Hướng dẫn chạy (Installation & Usage)
# Clone dự án
* git clone <your_repo_url>
* cd shopping_cart_analysis

# Cài đặt các thư viện phụ thuộc
* pip install -r requirements.txt
2. Chuẩn bị dữ liệu
Tải file dữ liệu online_retail.csv và đặt vào thư mục: data/raw/online_retail.csv

3. Chạy dự án
Bạn có hai cách để chạy dự án:

Cách 1: Chạy tự động (Khuyên dùng) Sử dụng script run_papermill.py để chạy tuần tự các notebook từ làm sạch đến sinh luật.

python run_papermill.py
Cách 2: Chạy từng Notebook Mở Jupyter Lab/Notebook và chạy lần lượt:

notebooks/preprocessing_and_eda.ipynb

notebooks/basket_preparation.ipynb

notebooks/apriori_modelling.ipynb (hoặc topic3_weighted_analysis.ipynb)

🔧 Công nghệ sử dụng (Tech Stack)
Python: Ngôn ngữ lập trình chính.

Pandas: Xử lý dữ liệu bảng và tính toán trọng số.

MLxtend: Thư viện triển khai Apriori và Association Rules.

NetworkX: Vẽ biểu đồ mạng lưới (Network Graph).

Plotly: Vẽ biểu đồ tương tác (Interactive Charts).

Papermill: Tự động hóa quy trình chạy Notebook.

👥 Tác giả (Author)
Project được thực hiện bởi: Trang Le

Dự án môn học: Khai phá dữ liệu (Data Mining)
Nhóm 5 CNTT 17-10 phát triển 
Chủ đề nghiên cứu: Phân tích giỏ hàng & Weighted Association Rules.
📄 License MIT — sử dụng tự do cho nghiên cứu, học thuật và ứng dụng nội bộ.
