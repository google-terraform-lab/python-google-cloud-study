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

fake = Faker()
time_window_start = datetime.now(timezone.utc) - timedelta(days=1)
time_window_end = datetime.now(timezone.utc)
movies = ['Movie A', 'Movie B', 'Movie C', 'Movie D', 'Movie E']

def generate_movie_sessions(num_sessions=3):
    sessions = []
    for _ in range(num_sessions):
        movie = random.choice(movies)
        start_time = fake.date_time_between(start_date=time_window_start, end_date=time_window_end, tzinfo=timezone.utc)
        end_time = start_time + timedelta(hours=random.randint(1, 3))
        sessions.append({
            "movie": movie,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
    return sessions

def generate_fake_data():
    return {
        "name": fake.name(),
        "email": fake.email(),
        "timestamp": fake.date_time_between(start_date=time_window_start, end_date=time_window_end, tzinfo=timezone.utc).isoformat(),
        "value": random.randint(1, 100),
        "sessions": generate_movie_sessions()
    }

def flush_futures(futures):
    for future in as_completed(futures):
        try:
            result = future.result()
            print(f"Published message ID: {result}")
        except Exception as e:
            print(f"Failed to publish message: {e}")

def publish_sessions(data):
    with pubsub_v1.PublisherClient() as client:
        futures = []
        for session in data['sessions']:
            message = json.dumps(session).encode()
            future = client.publish(session_topic_name, message)
            futures.append(future)
        flush_futures(futures)

def publish_movies():
    with pubsub_v1.PublisherClient() as client:
        futures = []
        for movie in movies:
            movie_data = {"movie": movie}
            message = json.dumps(movie_data).encode()
            future = client.publish(movie_topic_name, message)
            futures.append(future)
        flush_futures(futures)

with pubsub_v1.PublisherClient() as client:
    futures = []
    for _ in range(100):
        message_dict = generate_fake_data()
        message = json.dumps(message_dict).encode()
        future = client.publish(topic_name, message)
        futures.append(future)

        publish_sessions(message_dict)

        if len(futures) > 1000:
            flush_futures(futures)
            futures = []

    flush_futures(futures)

publish_movies()