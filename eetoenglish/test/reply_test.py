#Tests replying to tweets
from dotenv import load_dotenv 
load_dotenv()
import os
import tweepy
from eetoenglish.stream_listener.StreamListener import StreamListener
from urllib3.exceptions import ProtocolError

auth = tweepy.OAuthHandler(os.environ["CONSUMER_TOKEN"], os.environ["CONSUMER_SECRET"])
auth.set_access_token(os.environ["KEY"], os.environ["SECRET"])

api = tweepy.API(auth)

streamlistener = StreamListener(api)
stream = tweepy.Stream(auth=api.auth, listener=streamlistener)
while True:
    try:
        stream.filter(follow=['19765204',],track=['#EEBOTTEST'],stall_warnings=True)
    except (ProtocolError):
        continue



 





