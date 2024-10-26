from google.cloud import pubsub_v1
import json

publisher = pubsub_v1.PublisherClient()

project_id = "personal-433817"
topic_name = f"projects/{project_id}/topics/bye"


with pubsub_v1.PublisherClient() as client:

    for i in range(1_000):
        message = json.dumps({ "message": f"My message {i}!" }).encode()
        print(message)
        future = client.publish(topic_name, message, spam='eggs')
        future.result()