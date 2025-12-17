# Giải Mã "Sức Nâng" (Lift): Bí Quyết Biến Dữ Liệu Thành Doanh Thu Từ 541,909 Giao Dịch

## 🎯 Bài toán đặt ra

Bạn là Giám đốc Marketing của một chuỗi bán lẻ. Bạn có hàng ngàn quy luật kết hợp sản phẩm (Association Rules) từ dữ liệu lịch sử.

- **Luật A:** "Khách mua *Điện thoại* thường mua *Ốp lưng*" (Dễ đoán, ai cũng biết).
- **Luật B:** "Khách mua *Bia* thường mua *Tã lót*" (Huyền thoại trong ngành Data, nhưng liệu có thật?).
- **Luật C:** "Khách mua *Bình trà Green* chắc chắn mua *Bình trà Pink*" (Insight ngách).

Làm sao để không bị "ngộp" trong bể dữ liệu này? Làm sao biết luật nào **sinh ra tiền**, luật nào chỉ là **sự trùng hợp ngẫu nhiên**?

Câu trả lời nằm ở chỉ số **Lift (Độ nâng)**. Chúng tôi đã phân tích hơn nửa triệu giao dịch để phân loại và định giá trị thực sự của từng mối liên kết.

---

## 📊 Dữ liệu và Phương pháp

### Dataset
- **541,909 dòng dữ liệu** giao dịch từ bán lẻ trực tuyến (Online Retail UK).
- **Mục tiêu:** Tìm ra các cặp sản phẩm có mối liên kết "hữu cơ" thực sự, loại bỏ các yếu tố ngẫu nhiên.

### "Bộ lọc vàng" - Phân loại theo Lift

Thay vì nhìn vào tất cả các luật, chúng tôi chia chúng thành 3 nhóm chiến lược dựa trên **Lift** và **Support**:

| Nhóm Chiến Lược | Đặc điểm nhận dạng | Ý nghĩa kinh doanh |
|---|---|---|
| **1. Core Bundles** | **Support CAO - Lift CAO** | "Cặp đôi hoàn hảo". Sản phẩm bán chạy và luôn đi cùng nhau. |
| **2. Hidden Gems** | **Support THẤP - Lift CAO** | "Viên ngọc ẩn". Ít người mua, nhưng ai mua A thì chắc chắn mua B. |
| **3. The Trap** | **Confidence CAO - Lift ≈ 1** | "Bẫy ngẫu nhiên". Khách mua B vì B quá phổ biến, không phải vì mua A. |

---

## 📈 Kết Quả Phân Tích Thực Tế

Sau khi chạy thuật toán Apriori với ngưỡng tối ưu (Support > 1.5%, Lift > 2.0), chúng tôi thu được bức tranh thú vị:

### 1. Phân bổ các luật tìm được

![Biểu đồ phân tán Support vs Confidence](Scatter_Plot.png)

**Quan sát:**
- Tổng số luật tìm thấy: **516 luật**.
- **Nhóm 1 (Core Bundles):** 254 luật.
- **Nhóm 2 (Hidden Gems):** 257 luật.
- **Nhóm 3 (The Trap):** 0 luật (Do chúng tôi đã lọc Lift > 2.0 ngay từ đầu để loại bỏ rác).

**Ý nghĩa:** Số lượng luật "ngách" (Nhóm 2) chiếm tới ~50% tổng số luật. Nếu chỉ tập trung vào các sản phẩm bán chạy (Top sellers), ta đã bỏ lỡ một nửa cơ hội doanh thu từ các sản phẩm ngách này.

### 2. So sánh hiệu quả giữa các nhóm

| Chỉ số trung bình | Nhóm 1 (Core) | Nhóm 2 (Niche) | Nhận xét |
|---|---|---|---|
| **Lift** | ~27.5 | **~39.5** | Nhóm ngách có liên kết mạnh hơn hẳn! |
| **Confidence** | ~77% | **~83%** | Khách ngách trung thành hơn khách đại trà. |
| **Support** | ~1.8% | ~1.5% | Chênh lệch không quá lớn về độ phổ biến. |

**Bất ngờ lớn:** Các sản phẩm ngách (Nhóm 2) tuy ít người mua hơn, nhưng **sức mạnh liên kết (Lift) cao gấp 1.4 lần** so với nhóm bán chạy.

---

## 💡 5 Insight Chất Lượng & Hành Động

### **1. Đừng để bị lừa bởi Confidence cao (Bẫy Nhóm 3)**
- **Insight:** Một luật có Confidence 90% (Mua A thì 90% mua B) nghe có vẻ hấp dẫn. Nhưng nếu B là "Túi nilon" hay sản phẩm best-seller mà ai cũng mua, thì Lift sẽ xấp xỉ 1.
- **Hành động:** **Dừng khuyến mãi** cho các cặp này. Khách sẽ mua B dù bạn có giảm giá hay không. Đừng ném tiền qua cửa sổ.

### **2. Mỏ vàng nằm ở "Đuôi dài" (Long-tail)**
- **Insight:** Nhóm 2 (Support thấp, Lift cực cao - ví dụ: Bộ tách trà *Regency Green* & *Roses*) đại diện cho nhóm khách hàng có "gu" riêng. Họ mua ít nhưng mua theo bộ.
- **Hành động:** Sử dụng **Personalized Recommendation** (Gợi ý cá nhân hóa) qua Email hoặc App. Đừng bày ra trang chủ (tốn diện tích), hãy "thì thầm" vào đúng tai người cần.

### **3. Chiến thuật "Cross-merchandising" cho Nhóm 1**
- **Insight:** Nhóm 1 (Support cao, Lift cao) là dòng tiền chính (Cash cows). Dữ liệu chỉ ra cặp đôi: **Small Marshmallows Pink Bowl** và **Dolly Mix Design Orange Bowl**.
- **Hành động:** Thay đổi **Store Layout**. Đặt hai kệ hàng này sát cạnh nhau hoặc tạo các **"Combo Tiệc Tùng"** (Bundle) giảm giá 5-10% để tăng giá trị đơn hàng trung bình (AOV) ngay lập tức.

### **4. Lift cao > 30 là dấu hiệu của "Sản phẩm thay thế" hoặc "Bộ sưu tập"**
- **Insight:** Các luật có Lift đột biến (>30) thường rơi vào các biến thể màu sắc (Xanh - Đỏ) hoặc các phần của một bộ sưu tập (Đĩa - Tách - Lọ).
- **Hành động:** Thiết kế UI/UX cho phép **"Shop the Look"** (Mua cả bộ sưu tập) chỉ với 1 cú click chuột, thay vì bắt khách hàng tìm lẻ tẻ từng món.

### **5. Quy luật "Mỏ neo" trong định giá**
- **Insight:** Khi một sản phẩm A có liên kết Lift cao với B (như *Charlotte Bag* các mẫu khác nhau), khách hàng thường có xu hướng sưu tầm.
- **Hành động:** Tăng giá nhẹ sản phẩm bán chạy nhất (Anchor), nhưng tặng kèm/giảm giá sản phẩm biến thể ít người mua hơn để giải phóng hàng tồn kho mà khách vẫn cảm thấy được "hời".

---

## 🎁 Case Study: Bộ Đĩa Regency - Sức Mạnh Của Nhóm Ngách

Dữ liệu chỉ ra một cặp luật thuộc **Nhóm 2 (Hidden Gems)** cực kỳ ấn tượng:

**Luật:** `REGENCY TEA PLATE GREEN` ↔ `REGENCY TEA PLATE ROSES`

- **Lift: 39.55** (Liên kết siêu bền chặt - cao nhất trong các luật tìm thấy)
- **Confidence: 83.6%**
- **Support: ~1.5%**

**Phân tích:** Chỉ có 1.5% khách hàng mua loại đĩa này. NHƯNG, đã mua đĩa màu Xanh thì 83.6% sẽ mua thêm đĩa màu Hồng. Gần như không ai mua lẻ.

- **Quyết định quản lý sai lầm cũ:** Thấy Support thấp -> Nghĩ là hàng tồn kho -> Bán xả hàng lẻ tẻ.
- **Quyết định mới dựa trên Data:** Đóng gói thành **"Bộ sưu tập Trà Chiều Vintage"** (Set 4 cái: 2 Xanh, 2 Hồng). Bán giá cao hơn, định vị phân khúc cao cấp.

---

## 📌 Kết Luận và Khuyến Nghị

Để tối ưu hóa doanh thu dựa trên luật kết hợp, hãy áp dụng chiến thuật **"3 Tầng"**:

1.  **Tầng Đại Trà (Nhóm 1):** Tối ưu hóa trưng bày, làm Combo quà tặng (như Marshmallows & Dolly Mix). Đây là nguồn thu ổn định.
2.  **Tầng Chuyên Sâu (Nhóm 2):** Tiếp thị lại (Retargeting) chính xác, bán theo bộ sưu tập (Collection - như Regency Tea Plate). Đây là nguồn lợi nhuận biên cao.
3.  **Tầng Cảnh Báo (Nhóm 3):** Rà soát và cắt giảm khuyến mãi thừa thãi. Đây là nơi tiết kiệm chi phí.

> **"Đừng chỉ bán những gì khách hàng muốn mua. Hãy bán những gì đi kèm với thứ họ vừa bỏ vào giỏ."**

---
**Nhóm thực hiện:** Nhóm 5 - CNTT 17-10
**Công cụ:** Python, Mlxtend, Apriori Algorithm
