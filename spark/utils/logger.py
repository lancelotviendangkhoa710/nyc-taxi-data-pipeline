import logging
import sys

def get_logger(name: str) -> logging.Logger:

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
        
   
        
    return logger
