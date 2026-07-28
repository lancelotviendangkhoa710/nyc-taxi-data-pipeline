import os
import sys
import requests
from datetime import datetime
from pathlib import Path

RAW_DATA_DIR = Path("data/raw/yellow")

def fetch_data(start_date, end_date):
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    current = datetime.strptime(start_date, "%Y-%m")
    end = datetime.strptime(end_date, "%Y-%m")
    
    while current <= end:
        date_str = current.strftime("%Y-%m")
        filename = f"yellow_tripdata_{date_str}.parquet"
        filepath = RAW_DATA_DIR / filename
        
        if filepath.exists():
            print(f"Skip: {filename} đã tồn tại.")
        else:
            url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{filename}"
            print(f"Downloading: {url}")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:
                print(f"Error: {response.status_code} - {url}")
        
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fetch_taxi_data.py <start_date> <end_date>")
        fetch_data(sys.argv[1], sys.argv[2])

