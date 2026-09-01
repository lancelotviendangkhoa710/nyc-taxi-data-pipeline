import os
import sys
import requests
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from datetime import datetime
from spark.config import RAW_DIR
from spark.utils.logger import get_logger

logger = get_logger(__name__)

DATA_START_DATE = "2025-06"  

def _current_month() -> str:
    return datetime.now().strftime("%Y-%m")

def _check_needs_download(url: str, filepath) -> bool:
    try:
        response = requests.head(url, timeout=15, allow_redirects=True)
        if response.status_code != 200:
            logger.warning("HEAD %s -> %s - using local file.", url, response.status_code)
            return False
    except Exception as e:
        logger.warning("Could not connect to server %s: %s - using local file.", url, e)
        return False

    local_size = os.path.getsize(filepath)
    local_mtime = os.path.getmtime(filepath)

    content_length = response.headers.get("Content-Length")
    if content_length is not None:
        remote_size = int(content_length)
        if remote_size != local_size:
            logger.info("Size mismatch (local=%d, remote=%d) -> update required.", local_size, remote_size)
            return True

    last_modified = response.headers.get("Last-Modified")
    if last_modified is not None:
        try:
            remote_ts = parsedate_to_datetime(last_modified).timestamp()
            if remote_ts > local_mtime:
                local_dt = datetime.fromtimestamp(local_mtime, tz=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
                logger.info("Server is newer (remote=%s, local=%s) -> update required.", last_modified, local_dt)
                return True
        except Exception as e:
            logger.warning("Could not parse Last-Modified '%s': %s", last_modified, e)

    return False

def _download_file(url: str, filepath) -> bool:
    logger.info("Downloading: %s", url)
    response = requests.get(url, stream=True, timeout=60)
    if response.status_code == 200:
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info("Downloaded successfully: %s", filepath.name)
        return True
    elif response.status_code == 404:
        logger.warning("Data not yet available on server: %s (404) - skipping.", filepath.name)
        return False
    else:
        logger.error("Error: %s - %s", response.status_code, url)
        return False

def fetch_data(start_date: str = DATA_START_DATE, end_date: str = None) -> None:
    if end_date is None:
        end_date = _current_month()

    limit_start = datetime.strptime(DATA_START_DATE, "%Y-%m")
    try:
        requested_start = datetime.strptime(start_date, "%Y-%m")
    except ValueError as e:
        logger.error("Invalid start_date: %s. Use YYYY-MM.", e)
        raise

    if requested_start < limit_start:
        logger.warning(
            "start_date %s is earlier than threshold %s, adjusting to %s.",
            start_date, DATA_START_DATE, DATA_START_DATE,
        )
        start_date = DATA_START_DATE

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    try:
        current = datetime.strptime(start_date, "%Y-%m")
        end = datetime.strptime(end_date, "%Y-%m")
    except ValueError as e:
        logger.error("Invalid date format: %s. Use YYYY-MM.", e)
        raise

    logger.info("Fetching data from %s to %s.", start_date, end_date)

    while current <= end:
        date_str = current.strftime("%Y-%m")
        filename = f"yellow_tripdata_{date_str}.parquet"
        filepath = RAW_DIR / filename
        url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{filename}"

        if filepath.exists():
            if _check_needs_download(url, filepath):
                logger.info("Deleting old file, downloading new version: %s", filename)
                filepath.unlink()
                try:
                    _download_file(url, filepath)
                except Exception as e:
                    logger.error("Failed to download %s: %s", url, e)
                    raise
            else:
                logger.info("Skip: %s is already up to date.", filename)
        else:
            try:
                _download_file(url, filepath)
            except Exception as e:
                logger.error("Failed to download %s: %s", url, e)
                raise

        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

if __name__ == "__main__":
    fetch_data()
