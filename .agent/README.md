# 🤖 AI Agent Instructions — NYC Taxi Data Engineering Project

> **⚠️ ĐỌC FILE NÀY TRƯỚC TIÊN.** Đây là entry point cho mọi AI agent làm việc với dự án này.
> Sau khi đọc file này, đọc tiếp các file trong thư mục `.agent/` theo thứ tự được chỉ định.

---

## Thứ Tự Đọc Bắt Buộc

```
1. .agent/README.md          ← (file này) — Overview & index
2. .agent/project.md         ← Kiến trúc, stack, business context
3. .agent/conventions.md     ← Coding conventions & naming rules
4. .agent/commit.md          ← Git commit standards (QUAN TRỌNG)
5. .agent/workflow.md        ← ETL workflow, phase hiện tại, next steps
6. .agent/decisions.md       ← Architectural decisions & design choices
7. context.md                ← Full project context (root level)
```

---

## Tóm Tắt Nhanh (30 giây)

| Thuộc tính | Giá trị |
|---|---|
| **Dự án** | NYC Taxi Data Engineering Pipeline |
| **Phase hiện tại** | Phase 2 — Spark ETL (⏳ In Progress) |
| **Language** | Python 3.10+ |
| **Processing** | PySpark (Local mode `local[*]`) |
| **Warehouse** | Google BigQuery (Sandbox) |
| **Transform** | dbt với adapter dbt-bigquery |
| **Orchestration** | Apache Airflow |
| **OS** | Windows (dev), Linux (prod/Docker) |

---

## Nguyên Tắc Vàng Cho AI

1. **KHÔNG bao giờ hardcode paths** — Dùng `spark/config.py`
2. **KHÔNG sửa code production mà không có tests** — Đặt câu hỏi trước
3. **KHÔNG tạo file mới nếu đã có pattern** — Tìm trong `spark/utils/`
4. **LUÔN commit đúng chuẩn** — Đọc `.agent/commit.md`
5. **LUÔN hỏi trước khi thay đổi architecture** — Đây là dự án học tập

---

## Cấu Trúc Thư Mục Quan Trọng

```
NYC_Taxi_Prj/
├── .agent/                  ← AI instructions (thư mục này)
├── spark/
│   ├── config.py            ← ⭐ Single source of truth cho config
│   ├── etl/
│   │   ├── extract.py       ← Đọc parquet
│   │   ├── validate.py      ← Data quality checks
│   │   ├── transform.py     ← Clean + derive columns
│   │   └── [load.py]        ← TODO: Ghi ra processed
│   └── utils/
│       └── logger.py        ← Logging module (dùng lại)
├── docs/                    ← Documentation (phases, schema, model)
├── data/
│   ├── raw/                 ← Parquet gốc (KHÔNG sửa)
│   └── processed/           ← Output của ETL
├── warehouse/               ← BigQuery DDL schemas
├── dbt/                     ← dbt models (staging/intermediate/mart)
├── airflow/dags/            ← Airflow DAGs
└── context.md               ← Full context document
```

---

## Liên Hệ / Metadata

- **Người tạo:** Data Engineering Learner (Portfolio Project)
- **Mục tiêu:** Internship/Job preparation
- **Cập nhật lần cuối:** 2026-07-08
