import gzip
import io
import os
from google.cloud import storage
import json
from datetime import datetime, timedelta

bucket_name = os.getenv("BUCKET_NAME")
topic_name = os.getenv("TOPIC_NAME")
start_date = os.getenv("START_DATE")
inclusive = bool(os.getenv("INCLUSIVE", "1"))

output_prefix = 'processed-messages'

_, project_id, _, folder_path = topic_name.split("/")

client = storage.Client()


def interpolate_dates(start_date: str, inclusive: bool = False):
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    if inclusive:
        end_date_dt = datetime.now()
    else:
        end_date_dt = datetime.now() - timedelta(days=1)

    date_list = []
    current_date = start_date_dt
 
    while current_date <= end_date_dt:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    return date_list


def compact_messages_by_hour(bucket_name: str, folder_path: str, date: str, output_prefix: str):
    bucket = client.get_bucket(bucket_name)
    
    for hour in range(24):
        prefix = f'{folder_path}/{date}/{hour:02}/'
        blobs = client.list_blobs(bucket, prefix=prefix)

        sorted_blobs = sorted(blobs, key=lambda x: x.name)
        print(prefix, len(sorted_blobs))
        compacted_data = []
        for blob in sorted_blobs:
            content = blob.download_as_bytes()
            for line in content.decode().split("\n"):
                if line:
                    compacted_data.append(json.loads(line))
        
        if compacted_data:
            output_data = json.dumps(compacted_data).encode('utf-8')
            blob_path = f'{output_prefix}/{date}/{hour:02}.json'
            output_blob = bucket.blob(blob_path)
            output_blob.upload_from_string(output_data) # not compacted
            print(f"Data compacted and saved to {blob_path}")

            buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=buffer, mode='wb') as gz:
                gz.write(output_data)
            buffer.seek(0)

            compacted_blob_path = f'{output_prefix}/{date}/{hour:02}.json.gz'
            output_blob = bucket.blob(compacted_blob_path)
            output_blob.upload_from_file(buffer, content_type='application/gzip')
            print(f"Data compacted and saved to {compacted_blob_path}")

def main():
    for date in interpolate_dates(start_date=start_date, inclusive=inclusive):
        print(f"Inspecting {date}")

        compact_messages_by_hour(
            bucket_name=bucket_name, 
            folder_path=folder_path, 
            date=date, 
            output_prefix=output_prefix
        )

if __name__ == "__main__":
    main()
