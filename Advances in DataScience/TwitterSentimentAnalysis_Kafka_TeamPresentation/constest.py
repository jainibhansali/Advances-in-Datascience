import sys
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from uuid import uuid1
from pyspark.sql.types import StructType
from pyspark.sql.types import StructField
from pyspark.sql.types import StringType
import pyspark
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pyspark.sql import SQLContext
from pyspark.sql import Row

if __name__ == '__main__':
	sc = SparkContext(appName='PythonStreamingRecieverKafkaWordCount')
	ssc = StreamingContext(sc, 2) # 2 second window
	#broker, topic = sys.argv[1:]
	analyzer = SentimentIntensityAnalyzer()
	kvs = KafkaUtils.createStream(ssc,'localhost:2181',"test-consumer-group",{'test':1}) 
	parsed = kvs.map(lambda v: json.loads(v[1]))
	authors_loc = parsed.map(lambda tweet: tweet['user']['location'])
	authors_tweet = parsed.map(lambda tweet: analyzer.polarity_scores(tweet['text'].encode('utf-8')))
	tweettext=parsed.map(lambda tweet: tweet['text'].encode('utf-8'))
	finscore=authors_tweet.map(lambda score:score['compound'])
	tweettext.pprint()
	finscore.pprint()
	authors_loc.pprint()
	ssc.start()
	ssc.awaitTermination()