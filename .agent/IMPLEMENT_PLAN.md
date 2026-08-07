# IMPLEMENT PLAN: Thêm Rule Tạo Document Cập Nhật Tiến Độ Công Việc

## 1. Mục Tiêu

Tạo một rule (quy tắc) trong hệ thống AI để:
- Tự động gợi ý cập nhật document tiến độ (`docs/progress/PROGRESS.md`) mỗi khi hoàn thành task/commit mới
- Ghi lại milestone, deliverable, task status, blockers, risks, và performance metrics
- Thực hiện theo quy trình: AI gợi ý → Người dùng review → Approve trước khi lưu

## 2. Phạm Vi (Scope)

### Sẽ Làm:
1. Tạo thư mục `docs/progress/` (nếu chưa có)
2. Tạo template document `docs/progress/PROGRESS.md` với cấu trúc chuẩn
3. Thêm rule "Progress Tracking" vào file `.agent/workflow.md`
4. Cập nhật `.agent/README.md` để liệt kê thứ tự đọc bao gồm progress tracking rule
5. Tạo rule trong `.agent/` hoặc hướng dẫn trong `MASTER_CONTEXT.md` về cách trigger cập nhật

### Không Làm:
- Tự động commit hoặc push (chỉ gợi ý)
- Thay đổi cấu trúc folder hiện tại (ngoài `docs/progress/`)
- Viết script automation (chỉ quy tắc cho AI)

## 3. Các Bước Chi Tiết

### Bước 1: Tạo thư mục docs/progress/
- Tạo folder: `d:\NYC_Taxi_Project\docs\progress\`
- Tạo file PROGRESS.md với template

### Bước 2: Tạo template PROGRESS.md
Cấu trúc:
```
# Project Progress Tracking — NYC Taxi Data Engineering

## Current Status (Trạng thái hiện tại)
- Current Phase: Phase X
- Last Updated: YYYY-MM-DD HH:MM
- Overall Progress: X%

## Milestones Completed ✅
| # | Milestone | Date | Status | Notes |
|---|-----------|------|--------|-------|
| 1 | Task 1 | YYYY-MM-DD | Done | Link to commit |

## Current Tasks 🔄 (In Progress)
| # | Task | Assignee | Status | Blockers |
|---|------|----------|--------|----------|

## Upcoming Tasks 📋 (TODO)
| # | Task | Priority | Effort |
|---|------|----------|--------|

## Blockers & Risks ⚠️
| ID | Issue | Severity | Resolution |
|----|-------|----------|-----------|

## Performance Metrics 📊
| Metric | Value | Date |
|--------|-------|------|

## Phase Roadmap
Phase 1 → Phase 2 → Phase 3 → Phase 4

## Notes
```

### Bước 3: Thêm rule vào .agent/workflow.md
Thêm mục "Progress Tracking Rule" trước "Next Phase Preview"
Nội dung: Hướng dẫn AI khi nào gợi ý cập nhật, format cập nhật, quy trình approval

### Bước 4: Cập nhật .agent/README.md
- Thêm `8. .agent/workflow.md (Progress Tracking Rules)` vào "Thứ Tự Đọc Bắt Buộc"
- Thêm mục "Progress Tracking Rules" mới trong file
- Mô tả: Khi nào AI gợi ý update, người dùng review trước khi lưu

### Bước 5: Cập nhật CURRENT_STATE.md
Chuyển STATE từ 1 (INQUIRY) sang 2 (PLANNING)
Ghi nhận yêu cầu: "Thêm rule tạo document cập nhật tiến độ công việc"

## 4. Ràng Buộc & Quy Tắc

- Document phải theo format Markdown
- Mỗi update phải có timestamp
- AI sẽ gợi ý sau mỗi commit/task hoàn thành
- Người dùng review trước khi lưu (hybrid model)
- File không được hardcode - dùng relative path: `docs/progress/PROGRESS.md`

## 5. Deliverables

1. ✅ Folder `docs/progress/` được tạo
2. ✅ File `docs/progress/PROGRESS.md` với template
3. ✅ Rule "Progress Tracking" thêm vào `.agent/workflow.md`
4. ✅ `.agent/README.md` cập nhật:
   - Thêm vào "Thứ Tự Đọc Bắt Buộc"
   - Thêm mục "Progress Tracking Rules" mới
5. ✅ `.agent/CURRENT_STATE.md` cập nhật sang STATE 2

## 6. Success Criteria

- [ ] Document template sẵn sàng
- [ ] Rule được tài liệu hóa rõ ràng trong workflow.md
- [ ] README.md được cập nhật với thứ tự đọc mới
- [ ] Người dùng có thể hiểu cách trigger progress update
- [ ] Không có lỗi Markdown syntax
- [ ] Có thể extend sau này khi cần

