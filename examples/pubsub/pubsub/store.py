import os
import json
import gzip
from datetime import datetime, timedelta, timezone
from google.cloud import pubsub_v1, storage
import hashlib

pubsub_client = pubsub_v1.SubscriberClient()
storage_client = storage.Client()

BUCKET_NAME = os.getenv("BUCKET_NAME")
subscription_path = os.getenv("SUBSCRIPTION_PATH")

seen_messages = set()
messages_to_ack = []

def write_to_gcs(date, data):
    gcs_path = f"{date}/data.json.gz"
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(gcs_path)
    
    compressed_data = gzip.compress(json.dumps(data).encode("utf-8"))
    blob.upload_from_string(compressed_data, content_type="application/gzip")

def process_message(message):
    data = json.loads(message.data)
    message_hash = hashlib.md5(message.data).hexdigest()

    if message_hash in seen_messages:
        return

    now = datetime.now(timezone.utc)
    start_of_yesterday = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_yesterday = start_of_yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    message_publish_time = message.publish_time.astimezone(timezone.utc)

    if not (start_of_yesterday <= message_publish_time <= end_of_yesterday):
        return

    seen_messages.add(message_hash)
    date = start_of_yesterday.strftime("%Y-%m-%d")
    write_to_gcs(date, data)
    messages_to_ack.append(message)

def main():
    streaming_pull_future = pubsub_client.subscribe(subscription_path, callback=process_message)
    try:
        streaming_pull_future.result(timeout=60)  # Adjust timeout as needed
        for message in messages_to_ack:
            message.ack()
        print("All messages acknowledged successfully.")
    except Exception as e:
        print(f"An error occurred: {e}. No messages acknowledged.")
    finally:
        streaming_pull_future.cancel()

if __name__ == "__main__":
    main()
