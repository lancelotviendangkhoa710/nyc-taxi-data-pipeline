import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Khởi tạo và cấu hình logger chuẩn cho ETL pipeline.
    
    Tại sao không dùng `print()`?
    - `print()` không có timestamp, log levels (DEBUG, INFO, WARNING, ERROR) để lọc lỗi.
    - Trong hệ thống production (như Airflow, Docker, AWS), logs cần được định dạng chuẩn
      để các công cụ giám sát (monitoring tools) có thể phân tích và gửi cảnh báo khi có lỗi.
    - Khi chạy phân tán trên Spark cluster, `print()` ở worker nodes có thể không hiển thị
      ở driver node (nơi bạn theo dõi log). Logger giúp kiểm soát luồng ghi log tốt hơn.
    """
    logger = logging.getLogger(name)
    
    # Chỉ cấu hình nếu logger chưa có handlers (tránh ghi đúp log)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Định dạng: [Thời gian] [Tên module] [Level] - Lời nhắn
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Ghi log ra Console (Standard Output)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # TODO: Bạn có thể tự mày mò thêm FileHandler để ghi log ra file trong thư mục `logs/`
        
    return logger
