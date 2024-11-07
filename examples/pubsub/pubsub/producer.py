from google.cloud import pubsub_v1
import json
import random
from faker import Faker
from datetime import datetime, timedelta, timezone
import os

publisher = pubsub_v1.PublisherClient()
topic_name = os.getenv("TOPIC_NAME")

fake = Faker()
time_window_start = datetime.now(timezone.utc) - timedelta(days=1)
time_window_end = datetime.now(timezone.utc)

def generate_fake_data():
    return {
        "id": fake.uuid4(),
        "name": fake.name(),
        "email": fake.email(),
        "timestamp": fake.date_time_between(start_date=time_window_start, end_date=time_window_end, tzinfo=timezone.utc).isoformat(),
        "value": random.randint(1, 100)
    }

def create_data_with_repetitions(total_records=100, repetition_rate=0.1):
    data_list = []
    unique_data = [generate_fake_data() for _ in range(int(total_records * (1 - repetition_rate)))]
    repeated_data = random.choices(unique_data, k=int(total_records * repetition_rate))

    data_list.extend(unique_data)
    data_list.extend(repeated_data)
    random.shuffle(data_list)

    return data_list

def flush_futures(futures):
    for future in futures:
        try:
            result = future.result()
            print(f"Published message ID: {result} in {topic_name}")
        except Exception as e:
            print(f"Failed to publish message: {e}")

with pubsub_v1.PublisherClient() as client:
    futures = []
    for message_dict in create_data_with_repetitions(total_records=100_000, repetition_rate=0.3):
        message = json.dumps(message_dict).encode()
        print(message)
        future = client.publish(topic_name, message, spam='eggs')
        futures.append(future)

        if len(futures) > 1000:
            flush_futures(futures)
            futures=[]

    flush_futures(futures)
