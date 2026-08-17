import sys
import requests
from datetime import datetime

from spark.config import RAW_DIR
from spark.utils.logger import get_logger

logger = get_logger(__name__)


def fetch_data(start_date: str, end_date: str) -> None:

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        current = datetime.strptime(start_date, "%Y-%m")
        end = datetime.strptime(end_date, "%Y-%m")
    except ValueError as e:
        logger.error("Invalid date format: %s. Use YYYY-MM format.", e)
        raise
    
    while current <= end:
        date_str = current.strftime("%Y-%m")
        filename = f"yellow_tripdata_{date_str}.parquet"
        filepath = RAW_DIR / filename
        
        if filepath.exists():
            logger.info("Skip: %s đã tồn tại.", filename)
        else:
            url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{filename}"
            logger.info("Downloading: %s", url)
            
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    logger.info("Downloaded successfully: %s", filename)
                else:
                    logger.error("Error: %s - %s", response.status_code, url)
            except Exception as e:
                logger.error("Failed to download %s: %s", url, e)
                raise
        
        # Increment month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info("Usage: python fetch_taxi_data.py <start_date> <end_date>")
        logger.info("Example: python fetch_taxi_data.py 2024-01 2024-12")
        sys.exit(1)
    
    fetch_data(sys.argv[1], sys.argv[2])

