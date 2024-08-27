import os
from google.cloud import pubsub_v1
import argparse 

publisher = pubsub_v1.PublisherClient()

project_id = "personal-433817"
topic_name = f"projects/{project_id}/topics/hello"
subscription_name = f"projects/{project_id}/subscriptions/hello"


with pubsub_v1.PublisherClient() as client:
    
    try:
        client.create_topic(name=topic_name)
    except:
        pass

    for i in range(10):
        message = f"My message {i}!".encode()
        print(message)
        future = client.publish(topic_name, message, spam='eggs')
        future.result()


def callback(message):
    print(message.data)
    message.ack()

with pubsub_v1.SubscriberClient() as client:
    try:
        client.create_subscription(
            name=subscription_name,
            topic=topic_name
        )
    except:
        pass

    future = client.subscribe(subscription_name, callback)

    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()