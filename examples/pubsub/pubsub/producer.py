from google.cloud import pubsub_v1
import json
import random
from faker import Faker
from datetime import datetime, timedelta, timezone
from concurrent.futures import as_completed
import os

publisher = pubsub_v1.PublisherClient()
topic_name = os.getenv("TOPIC_NAME")
session_topic_name = os.getenv("SESSION_TOPIC_NAME")
movie_topic_name = os.getenv("MOVIE_TOPIC_NAME")

Faker.seed(0)
fake = Faker()

time_window_start = datetime.now(timezone.utc) - timedelta(days=1)
time_window_end = datetime.now(timezone.utc)

titles = ["Lord", "Lady", "Sir", "Dame", "Baron", "Baroness", "Count", "Countess", "Duke", "Duchess"]

users  = [ (i, fake.email()) for i in range(100)]
movies = [ (i, f"{random.choice(titles)} {fake.first_name()} of {fake.city()}") for i in range(50) ]


def generate_movie_sessions(num_sessions=3):
    sessions = []
    for _ in range(num_sessions):
        movie_id = random.choice(movies)[0]
        user_id = random.choice(users)[0]

        start_time = fake.date_time_between(start_date=time_window_start, end_date=time_window_end, tzinfo=timezone.utc)
        end_time = start_time + timedelta(hours=random.randint(1, 3))
        sessions.append({
            "movie_id": movie_id,
            "user_id": user_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
    return sessions

def flush_futures(futures, topic):
    for future in as_completed(futures):
        try:
            result = future.result()
            print(f"Published message ID: {result} on topic {topic}")
        except Exception as e:
            print(f"Failed to publish message: {e}")


with pubsub_v1.PublisherClient() as client:
    futures = []
    for id, email in users:
        payload = json.dumps({"id": id, "email": email}).encode()
        future = client.publish(topic_name, payload)
        futures.append(future)

        if len(futures) > 1000:
            flush_futures(futures, topic_name)
            futures = []

    flush_futures(futures, topic_name)
    futures = []

    for id, title in movies:
        payload = json.dumps({"id": id, "title": title}).encode()
        future = client.publish(movie_topic_name, payload)
        futures.append(future)

        if len(futures) > 1000:
            flush_futures(futures, movie_topic_name)
            futures = []

    flush_futures(futures, movie_topic_name)
    futures = []

    num_sessions = 3
    sessions = []
    for id, email in users:
        for _ in range(num_sessions):
            movie_id = random.choice(movies)[0]
            user_id = random.choice(users)[0]

            start_time = fake.date_time_between(start_date=time_window_start, end_date=time_window_end, tzinfo=timezone.utc)
            end_time = start_time + timedelta(hours=random.randint(1, 3))
            payload = json.dumps({
                "movie_id": movie_id,
                "user_id": user_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }).encode()

            future = client.publish(session_topic_name, payload)
            futures.append(future)
            
            if len(futures) > 1000:
                flush_futures(futures, session_topic_name)
                futures = []

    flush_futures(futures, session_topic_name)
    futures = []
