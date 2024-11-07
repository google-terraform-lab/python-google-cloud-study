from datetime import datetime, timedelta
from google.cloud import storage, pubsub_v1
import pytz
import os


new_york_timezone = pytz.timezone('America/New_York')

bucket_name = os.getenv("BUCKET_NAME")
topic_name = os.getenv("TOPIC_NAME")
target_date = os.getenv("FROM_DATE")

_, project_id, _, folder_prefix = topic_name.split("/")

storage_client = storage.Client()
pubsub_client = pubsub_v1.PublisherClient()

def publish_to_pubsub(data):
    future = pubsub_client.publish(
        topic_name, 
        data.encode("utf-8"),
        redrive="true"
    )
    print(f"Published message ID: {future.result()}")


def process_raw_files_in_folder(folder_prefix: str, date_str: str):
    folder_prefix = f"{folder_prefix}_raw/{date_str}/"
    bucket = storage_client.bucket(bucket_name)
    blobs = sorted(bucket.list_blobs(prefix=folder_prefix), key=lambda blob: blob.name)
    
    files_processed = False
    for blob in blobs:
        if not blob.name.endswith('/'):
            file_content = blob.download_as_text()
            print(f"Processing file: {blob.name}")
            print("-----------")
            for line in file_content.split("\n"):
                if line:
                    publish_to_pubsub(line)
            files_processed = True

    if not files_processed:
        print(f"No files found for date: {date_str}")


def process_dates_from_target(target_date_str):
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
    target_date = new_york_timezone.localize(target_date).astimezone(pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today = datetime.now(tz=new_york_timezone).astimezone(pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    current_date = target_date
    while current_date <= today:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"Processing folder for date: {date_str}")

        process_raw_files_in_folder(folder_prefix=folder_prefix, date_str=date_str)

        current_date += timedelta(days=1)

if __name__ == "__main__":
    process_dates_from_target(target_date)