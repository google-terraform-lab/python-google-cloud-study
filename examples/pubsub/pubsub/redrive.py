from datetime import datetime, timedelta
from google.cloud import storage, pubsub_v1
import os

bucket_name = os.getenv("BUCKET_NAME")
topic_name = os.getenv("TOPIC_NAME")
_, project_id, _, folder_path = topic_name.split("/")

storage_client = storage.Client()
pubsub_client = pubsub_v1.PublisherClient()

def publish_to_pubsub(data):
    future = pubsub_client.publish(
        topic_name, 
        data.encode("utf-8"),
        redrive="true"
    )
    print(f"Published message ID: {future.result()}")


def process_files_in_folder(date_str):
    folder_prefix = f"{folder_path}/{date_str}/"
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
    today = datetime.now()

    current_date = target_date
    while current_date <= today:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"Processing folder for date: {date_str}")

        process_files_in_folder(date_str)

        current_date += timedelta(days=1)

if __name__ == "__main__":
    target_date = "2024-10-26"
    process_dates_from_target(target_date)