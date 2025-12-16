import sys
import os
import pandas as pd
import numpy as np

# Thêm đường dẫn để import library nếu cần (tuỳ chỉnh theo cấu trúc máy bạn)
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from apriori_library import DataCleaner, BasketPreparer, AssociationRulesMiner, DataVisualizer
except ImportError:
    # Fallback nếu file library nằm cùng thư mục
    from apriori_library import DataCleaner, BasketPreparer, AssociationRulesMiner, DataVisualizer

def analyze_rules_business_value(rules_df):
    """
    Phân loại và đánh giá luật theo giá trị kinh doanh.
    """
    print("\n" + "="*50)
    print("PHÂN TÍCH LUẬT THEO GIÁ TRỊ KINH DOANH (TOPIC 3)")
    print("="*50)

    if rules_df is None or rules_df.empty:
        print("Không có luật nào để phân tích.")
        return

    # Tính các ngưỡng (thresholds) dựa trên thống kê mô tả
    median_support = rules_df['support'].median()
    high_lift_threshold = 3.0  # Giả định Lift > 3 là rất mạnh
    
    print(f"Ngưỡng phân loại: Median Support = {median_support:.4f}, High Lift > {high_lift_threshold}")

    # 1. Nhóm Support Cao, Lift Cao (Core Business / Bundles)
    group_1 = rules_df[
        (rules_df['support'] >= median_support) & 
        (rules_df['lift'] >= high_lift_threshold)
    ].sort_values('lift', ascending=False)

    # 2. Nhóm Support Thấp, Lift Cao (Niche / Long-tail)
    group_2 = rules_df[
        (rules_df['support'] < median_support) & 
        (rules_df['lift'] >= high_lift_threshold)
    ].sort_values('lift', ascending=False)

    # 3. Nhóm Confidence Cao, Lift thấp (~1) (Cẩn thận bẫy ngẫu nhiên)
    # Lưu ý: Trong thực tế, Lift ~ 1 tức là độc lập. Lift < 1 là tương quan âm.
    # Ở đây ta lọc các luật có Conf cao nhưng Lift không quá cao (ví dụ < 1.5)
    group_3 = rules_df[
        (rules_df['confidence'] > 0.6) & 
        (rules_df['lift'] < 1.5) & 
        (rules_df['lift'] > 0.8)
    ].sort_values('confidence', ascending=False)

    # --- Xuất báo cáo ---
    
    print(f"\n[NHÓM 1] SUPPORT CAO & LIFT CAO (SL: {len(group_1)})")
    print(">> Đề xuất: Tạo Combo, đặt kệ chính, Cross-sell mạnh.")
    if not group_1.empty:
        print(group_1[['rule_str', 'support', 'confidence', 'lift']].head(5).to_string(index=False))
    
    print(f"\n[NHÓM 2] SUPPORT THẤP & LIFT CAO - NICHE (SL: {len(group_2)})")
    print(">> Đề xuất: Recommendation System, Email Marketing cá nhân hóa.")
    if not group_2.empty:
        print(group_2[['rule_str', 'support', 'confidence', 'lift']].head(5).to_string(index=False))

    print(f"\n[NHÓM 3] CONFIDENCE CAO, LIFT THẤP (SL: {len(group_3)})")
    print(">> Đề xuất: Không khuyến mãi, đây là hàng phổ thông ngẫu nhiên.")
    if not group_3.empty:
        print(group_3[['rule_str', 'support', 'confidence', 'lift']].head(5).to_string(index=False))
    else:
        print("Không tìm thấy luật nào trong nhóm này (điều này tốt, ít luật rác).")

def main():
    # 1. Cấu hình đường dẫn
    DATA_PATH = "data/raw/online_retail.csv" 
    if not os.path.exists(DATA_PATH):
        DATA_PATH = "cuongkaa/nhom5_cntt_17-10/Nhom5_CNTT_17-10-a790f690dc4626f108a30dd556c498108fa173c4/data/raw/online_retail.csv"
        if not os.path.exists(DATA_PATH):
            print(f"Lỗi: Không tìm thấy file dữ liệu tại {DATA_PATH}")
            return

    # ... (Các bước 1, 2 giữ nguyên) ...
    print("Đang tải và làm sạch dữ liệu...")
    cleaner = DataCleaner(DATA_PATH)
    cleaner.load_data()
    df_uk = cleaner.clean_data()
    
    print("Đang chuẩn bị basket...")
    basket_preparer = BasketPreparer(df_uk)
    basket_preparer.create_basket()
    basket_bool = basket_preparer.encode_basket()
    
    # BƯỚC 3: KHAI PHÁ LUẬT
    print("Đang khai phá luật kết hợp...")
    miner = AssociationRulesMiner(basket_bool)
    
    # --- Scenario A (Chạy nhưng không dùng kết quả để phân tích sau này) ---
    print("\n--- Chạy Scenario A ---")
    miner.mine_frequent_itemsets(min_support=0.02)
    miner.generate_rules(metric="lift", min_threshold=1.0)
    
    # --- Scenario B (Dùng cho báo cáo) ---
    print("\n--- Chạy Scenario B: Min Sup=0.015, Min Lift=2.0 ---")
    miner.mine_frequent_itemsets(min_support=0.015)
    rules_b = miner.generate_rules(metric="lift", min_threshold=2.0)
    rules_b = rules_b[rules_b['confidence'] > 0.3] 
    
    # === [SỬA LỖI TẠI ĐÂY] ===
    miner.rules = rules_b
    # Phải gán lại rules_b bằng giá trị trả về của hàm này để lấy được cột 'rule_str'
    rules_b = miner.add_readable_rule_str() 
    
    print(f"Số lượng luật sau khi tinh chỉnh: {len(rules_b)}")

    # BƯỚC 4: PHÂN TÍCH KINH DOANH
    # Bây giờ rules_b đã có 'rule_str', hàm này sẽ chạy đúng
    analyze_rules_business_value(rules_b)

    # BƯỚC 5: TRỰC QUAN HÓA
    print("\nĐang vẽ biểu đồ...")
    viz = DataVisualizer()
    
    # Các hàm vẽ dùng miner.rules (đã được cập nhật đồng bộ ở trên rồi) nên vẫn chạy tốt
    print("1. Hiển thị Scatter Plot...")
    viz.plot_rules_support_confidence_scatter(miner.rules, title="Phân bố luật (Màu = Lift)")
    
    print("2. Hiển thị Top 10 luật theo Lift...")
    viz.plot_top_rules_lift(miner.rules, top_n=10)

    print("3. Hiển thị Network Graph...")
    try:
        viz.plot_rules_network(miner.rules, max_rules=30, min_lift=3.0)
    except Exception as e:
        print(f"Không thể vẽ Network graph: {e}")

if __name__ == "__main__":
    main()