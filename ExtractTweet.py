from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import csv
from collections import namedtuple


TWITTER_CONFIGS = 'config.json'


def get_twitter_configs():
    #load configuration file
    config = json.load(open(TWITTER_CONFIGS, 'r'))
    
    
    twitter_configs = namedtuple(
        'TwitterConfigs',
        'consumer_key, consumer_secret, access_token, access_token_secret,file_name,count')

    # Go to http://dev.twitter.com and create an app.
    # The consumer key and secret will be generated for you.
    twitter_configs.consumer_key = config["consumer_key"]
    twitter_configs.consumer_secret = config["consumer_secret"]
    
    # After the step above, you will be redirected to your app's page.
    # Create an access token under the the "Your access token" section.
    twitter_configs.access_token = config["access_token"]
    twitter_configs.access_token_secret = config["access_token_secret"]
    
    twitter_configs.file_name = config["file_name"]
    
    twitter_configs.count = config["count"]
    
    twitter_configs.filter = config["filter"]
    
    return twitter_configs



class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def __init__(self,count):    
        self.count=count
        self.index = 1
        
    
    def on_data(self, data):
        
        a = json.loads(data,encoding='utf-8')    
        if a['lang'] == 'en' and len(a['text']) > 100:
            special=[";",r"\r\n"]
        
            current=a['text']
            for curSpec in special:
                current.replace(curSpec,"")        
            current=unicode(current.encode('utf-8'), 'ascii', 'ignore')
            
            self.index=self.index+1
            print current
            writer.writerow([current])
        
        if self.index >= self.count:
            return False
        else:
            return True

    def on_error(self, status):
        print status



if __name__ == '__main__':
    twitter_configs = get_twitter_configs()
    count = twitter_configs.count
    l = StdOutListener(count)
    with open(twitter_configs.file_name, 'wb') as f:
        writer = csv.writer(f,delimiter='\t')

        auth = OAuthHandler(twitter_configs.consumer_key,
                               twitter_configs.consumer_secret)
        auth.set_access_token(twitter_configs.access_token,
                          twitter_configs.access_token_secret)

        stream = Stream(auth, l)
        
        if len(twitter_configs.filter) > 0:
            stream.filter(track=[twitter_configs.filter])
        else:
            # filter required
            stream.filter(track=["a"])
        