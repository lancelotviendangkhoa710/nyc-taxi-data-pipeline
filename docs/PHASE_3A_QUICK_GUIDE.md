# 🎓 PHASE 3A: Tóm Tắt Dễ Hiểu (TL;DR)

> Nếu bạn chỉ có 5 phút, đọc cái này!

---

## ❓ Phase 3A Là Gì?

**Phase 3A = Thêm 2 layers vào dbt project của bạn**

```
┌─────────────────┐
│  Staging Layer  │ ✅ Đã có (làm sạch dữ liệu)
└────────┬────────┘
         │
┌────────▼────────┐
│ Intermediate    │ ❌ Chưa có (Phase 3A)
│ Layer           │ Kết hợp bảng, tính toán logic
└────────┬────────┘
         │
┌────────▼────────┐
│ Marts Layer     │ ❌ Chưa có (Phase 3A)
│                 │ Final tables cho BI tools
└─────────────────┘
```

---

## 📚 Kinh Nghiệm So Sánh

### Staging (Bạn có rồi)
```sql
-- Ví dụ: stg_trip.sql
SELECT trip_id, fare_amount, total_amount
FROM fact_trip
WHERE trip_distance > 0  -- Lọc dữ liệu thô
```

**Việc:** Lọc, rename, làm sạch  
**Dùng cho:** dbt developers

---

### Intermediate (Phase 3A - Bước 1)
```sql
-- Ví dụ: int_trips_with_dimensions.sql
SELECT
    t.trip_id,
    t.fare_amount,
    v.vendor_name,           -- ← JOIN từ stg_vendor
    loc.zone as pickup_zone  -- ← JOIN từ stg_location
FROM stg_trip t
LEFT JOIN stg_vendor v ON ...
LEFT JOIN stg_location loc ON ...
```

**Việc:** JOIN bảng, kết hợp dimensions  
**Dùng cho:** dbt developers

---

### Marts (Phase 3A - Bước 2)
```sql
-- Ví dụ: fct_trip_summary.sql (materialized as TABLE)
SELECT
    trip_id,
    vendor_name,
    pickup_zone,
    fare_amount,
    CASE
        WHEN tip_amount/fare_amount > 0.2 THEN 'High'
        ELSE 'Low'
    END as tip_category
FROM int_trips_with_dimensions
```

**Việc:** Tạo TABLE cuối cùng, tối ưu cho query  
**Dùng cho:** Analysts, BI tools

---

## 🎯 Tại Sao Cần Phase 3A?

| Vấn đề | Giải Pháp |
|--------|----------|
| Analysts phải JOIN 5 bảng mỗi lần query | Intermediate làm sẵn JOINs |
| Query chậm (100M rows) | Marts là TABLE, có indexes |
| Khó bảo trì (logic ở nhiều chỗ) | Tập trung ở dbt layers |
| Không test được | dbt tests đảm bảo data quality |

---

## 🚀 Điều Gì Xảy Ra Sau Phase 3A?

**Trước:**
```sql
-- Analyst phải viết query phức tạp
SELECT vendor_name, COUNT(*) as trip_count
FROM fact_trip f
LEFT JOIN dim_vendor v ON f.vendor_key = v.vendor_key
LEFT JOIN dim_location l ON f.pickup_location_key = l.location_key
WHERE trip_distance > 0 AND fare_amount > 0
GROUP BY vendor_name
-- Query này chậm, khó bảo trì
```

**Sau:**
```sql
-- Analyst chỉ cần query table cuối cùng
SELECT vendor_name, COUNT(*) as trip_count
FROM fct_trip_summary
GROUP BY vendor_name
-- Query nhanh, data đã được test!
```

---

## 📋 Checklist Nhanh

**Folder & Files:**
- [ ] Tạo `dbt/models/intermediate/`
- [ ] Tạo `dbt/models/marts/`

**Intermediate Models:**
- [ ] `int_trips_with_dimensions.sql` (JOIN 4 tables)
- [ ] `int_trip_metrics_by_vendor.sql` (GROUP BY)
- [ ] `_int_models.yml` (descriptions + tests)

**Marts Models:**
- [ ] `fct_trip_summary.sql` (materialized = table)
- [ ] `fct_vendor_daily_metrics.sql` (metrics table)
- [ ] `_mart_models.yml` (descriptions + tests)

**Validation:**
- [ ] `dbt run` ✅
- [ ] `dbt test` ✅
- [ ] Check PostgreSQL ✅

---

## 💡 Key Points

1. **Staging** = VIEW, chuẩn bị dữ liệu
2. **Intermediate** = VIEW, kết hợp logic
3. **Marts** = TABLE, sẵn sàng cho BI
4. **Tests** = Đảm bảo data quality ở mỗi layer
5. **Performance** = Marts có indexes, nhanh hơn

---

## 🎁 Ví Dụ Mini

**Trước Phase 3A:**
- Bạn có: `fact_trip`, `dim_vendor`, `dim_location` (5 tables)
- Analysts phải: JOIN tất cả 5 tables
- Query: Chậm

**Sau Phase 3A:**
- `fct_trip_summary` TABLE có tất cả info (sẵn JOINs)
- Analysts chỉ cần: `SELECT * FROM fct_trip_summary`
- Query: Nhanh 🚀

---

## ❓ Câu Hỏi Thường Gặp

**Q: Tại sao cần 3 layers? Sao không tạo 1 table lớn?**  
A: 3 layers dễ bảo trì, test, reuse. 1 table lớn khó quản lý.

**Q: Intermediate cũng là VIEW, có ích gì?**  
A: Tách logic phức tạp, dễ debug, reuse cho nhiều marts.

**Q: Phải update Marts bao lâu 1 lần?**  
A: Mỗi lần `dbt run`. Có thể setup schedule với Airflow.

**Q: Tests cần bao lâu?**  
A: 1-2 phút chạy mỗi lần. Đảm bảo data quality đáng giá!

---

## 🎓 Lesson Học

**Modern data warehouse có 3 layers:**

```
RAW (từ source)
  ↓ (ETL - Spark)
STAGING (view)
  ↓ (dbt - Phase 3A)
INTERMEDIATE (view)
  ↓ (dbt - Phase 3A)
MARTS (table)
  ↓ (BI Tools)
ANALYTICS
```

**Phase 3A = Xây dựng Intermediate + Marts layers** ✨

---

## 📌 Tài Liệu Liên Quan

- `PHASE_3A_EXPLANATION.md` - Giải thích chi tiết
- `PHASE_3A_IMPLEMENTATION.md` - Step-by-step hướng dẫn
- `docs/data_model.md` - Star schema design
- `docs/architecture.md` - Overall architecture

---

**Ready to start Phase 3A?** 🚀

Hãy cho tôi biết nếu bạn muốn:
- ✅ Bắt đầu code Phase 3A ngay
- ❓ Hỏi thêm câu hỏi
- 📖 Đọc thêm chi tiết
