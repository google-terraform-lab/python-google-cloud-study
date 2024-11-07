import gzip
import io
import os
from google.cloud import storage
from datetime import datetime, timedelta, tzinfo
import pytz
new_york_timezone = pytz.timezone('America/New_York')

bucket_name = os.getenv("BUCKET_NAME")
topic_name = os.getenv("TOPIC_NAME")
start_date = os.getenv("START_DATE")
inclusive = bool(os.getenv("INCLUSIVE", "1"))


_, project_id, _, folder_prefix = topic_name.split("/")

client = storage.Client()

def interpolate_dates(start_date: str, inclusive: bool = False):
    ref_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    ref_date_dt_localized = new_york_timezone.localize(ref_date_dt).astimezone(pytz.utc)
    end_date_dt = datetime.now(tz=new_york_timezone).astimezone(pytz.utc)
    print(ref_date_dt_localized, end_date_dt, inclusive)

    date_list = []
    current_date = ref_date_dt_localized
 
    while current_date <= end_date_dt:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    if inclusive:
        date_list.append(end_date_dt.strftime('%Y-%m-%d'))

    print(date_list)
    return date_list

def save_partitioned(original_name: str, data: str, date: str, hour: int):
    bucket = client.get_bucket(bucket_name)

    output_data = data.encode('utf-8')
    blob_path = f'{original_name}_partitioned/day={date}/hour={hour:02}/data.json'
    output_blob = bucket.blob(blob_path)
    output_blob.upload_from_string(output_data)
    print(f"Data compacted and saved to {blob_path}")

def save_partitioned_and_compressed(original_name: str,data: str, date: str, hour: int):
    bucket = client.get_bucket(bucket_name)
    output_data = data.encode('utf-8')

    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb') as gz:
        gz.write(output_data)
    buffer.seek(0)

    compacted_blob_path = f'{original_name}_partitioned_and_compressed/day={date}/hour={hour:02}/data.json.gz'
    output_blob = bucket.blob(compacted_blob_path)
    output_blob.upload_from_file(buffer, content_type='application/gzip')
    print(f"Data compacted and saved to {compacted_blob_path}")

def compact_messages_by_hour(bucket_name: str, folder_path: str, date: str):
    bucket = client.get_bucket(bucket_name)
    
    for hour in range(24):
        origin_prefix = f'{folder_path}/{date}/{hour:02}/'
        blobs = client.list_blobs(bucket, prefix=origin_prefix)

        sorted_blobs = sorted(blobs, key=lambda x: x.name)
        print(origin_prefix, len(sorted_blobs))
        compacted_data = ""
        for blob in sorted_blobs:
            content = blob.download_as_bytes()
            for line in content.decode().split("\n"):
                if line:
                    compacted_data += line+"\n"
        
        if compacted_data:
            save_partitioned(original_name=folder_path, data=compacted_data, date=date, hour=hour)
            save_partitioned_and_compressed(original_name=folder_path, data=compacted_data, date=date, hour=hour)

def main():
    for date in interpolate_dates(start_date=start_date, inclusive=inclusive):
        print(f"Inspecting {date}")

        compact_messages_by_hour(
            bucket_name=bucket_name, 
            folder_path=folder_prefix + "_raw", 
            date=date, 
        )

if __name__ == "__main__":
    main()
