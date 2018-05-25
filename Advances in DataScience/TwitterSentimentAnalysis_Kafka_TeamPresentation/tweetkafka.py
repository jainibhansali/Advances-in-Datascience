#!/usr/bin/env python


# import required libraries
from kafka import SimpleProducer, KafkaClient
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

# Kafka settings
topic = b'test'
# setting up Kafka producer
client = KafkaClient('localhost:9092')
producer = SimpleProducer(client)


#This is a basic listener that just put received tweets to kafka cluster.
class StdOutListener(StreamListener):
    def on_data(self, data):
		producer.send_messages(topic, data.encode('utf-8'))
		#print data
		return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    print('running the twitter-stream python code')
    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler('consumer key', 'consumer secret key')
    auth.set_access_token('access key', 'access secret key')
    stream = Stream(auth, l)
    # Goal is to keep this process always going
    while True:
        try:
           # stream.sample()
            stream.filter(languages=["en"], track=['java','ruby','python'])
        except:
            pass
