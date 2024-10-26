from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()

project_id = "personal-433817"
subscription_name = f"projects/{project_id}/subscriptions/bye-1"


def callback(message):
    print(message.data)
    message.ack()

with pubsub_v1.SubscriberClient() as client:

    future = client.subscribe(subscription_name, callback)

    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()