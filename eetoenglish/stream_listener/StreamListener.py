from __future__ import unicode_literals
import tweepy
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import urllib3.request
from bs4 import BeautifulSoup

class StreamListener(tweepy.StreamListener):
    """Subclass of Tweepy SteamListener for reading URL articles 

    Custom SteamListener for accessing twitters streaming API and reading
    articles, replies to original tweet with contents of article 

    Attributes: 
        api: An object that contains twitter API object 
        appendage: A String that is added to the end of tweet segments
        hashtags: A String that is added to the end of tweet segments with hashtags
        tweet_size: An Integer that is the length of each tweet segment  
    """

    def __init__(self, api, appendage=' ',hashtags='',tweet_size=280):
        """init 

        Initialises SteamListener

        Args:
            self: An object that represents instance 
            api: An object that contains twitter API object 
            appendage: A String that is added to the end of tweet segments
            hashtags: A String that is added to the end of tweet segments with hashtags
            tweet_size: An Integer that is the length of each tweet segment 

        Returns:
            A custom tweepy stream listener 
        """
        super(StreamListener)
        self.api = api
        self.appendage = appendage
        self.hashtags = hashtags
        self.tweet_size = tweet_size

    def on_status(self,status):
        """Status event handler 

        Called when listener detects a new status has been posted, calls 
        convert tweet to read tweet 

        Args: 
            self: An object that represents instance 
            status: An object that represents a tweet 
        """
        self.convertTweet(status)

    def on_error(self, status_code):
        """Error event handler 

        Called when an error occurs. returns twitter api status code 
        prints status code 

        Args: 
            self: An object that represents instance 
            status_code: An integer representing twitter api status code
        """
        print(status_code)

    def convertTweet(self,status):
        """Reads articles from URL within a tweet 

        Reads the first URL within a tweet and replies to status with text from article

        Args: 
            self: An object that represents instance 
            status: An object that represents a tweet 
        """
        #Variables
        tweet_id = status.id
        screen_name = "@"+status.user.screen_name;
        try:
            url = status.entities['urls'][0]['url']
        except IndexError:
            return
        #Convert content into tweets
        content = self.getHTMLContent(url)
        sentences = self.splitIntoSentences(content)
        tweets = self.createTweets(sentences, screen_name)
        self.postTweets(tweet_id,tweets)

    def getHTMLContent(self,url):
        response = urllib3.PoolManager().request("GET",url)
        parsed_html = BeautifulSoup(response.data.decode('utf-8'),features="html.parser")
        content = parsed_html.body.find('div', attrs={'class':'lightbox-content'})
        return content

    def splitIntoSentences(self,content):
        #Get all paragraphs 
        try:
            paragraphs = content.find_all('p')
        except AttributeError:
            return
        content_string = ""
        for p in paragraphs:
            content_string += p.text
        delimiter = "."
        sentences = [sentence+delimiter for sentence in content_string.split(delimiter) if sentence]
        return sentences

    def createTweets(self, sentences, screen_name):
        tweets = [screen_name + " This tweet was brought to you by @AldoAbdn"]
        sentence_index = 0
        tweet_index = 1
        #While we haven't gone through all the sentences 
        while sentence_index < (len(sentences)-1):
            #If we are starting a new tweet
            if len(tweets)==tweet_index:
                #If sentence + appendage is not greater than tweet size
                if(len(sentences[sentence_index])+len(self.appendage) <= self.tweet_size):
                    tweets.insert(tweet_index,sentences[sentence_index]+self.appendage)
                    sentence_index+=1
                #Else if sentence itself is short enough
                elif(len(sentences[sentence_index])<=self.tweet_size):
                    tweets.insert(tweet_index,sentences[sentence_index]+self.appendage)
                    sentence_index+=1
                #Else sentence is too long and needs split up
                else:
                    sentence = sentences[sentence_index]
                    words = sentence.split()
                    split_sentences = [""]
                    split_index = 0
                    #Put words into new sentences
                    for word in words:
                        if(split_sentences[split_index]+len(word)<=self.tweet_size):
                            split_sentences[split_index] += word
                        else:
                            split_index+=1
                            split_sentences[split_index] = ""
                    #Add sentences to original list 
                    for x in range(len(split_sentences)):
                        sentences[sentence_index + x].insert(x,split_sentences)
            #Else if the combined size is greater than the tweet size, start a new tweet 
            elif len(tweets[tweet_index]) + len(sentences[sentence_index]) + len(self.appendage) > self.tweet_size:
                #If there is room, add hashtags to end
                if len(tweets[tweet_index])+len(self.hashtags)<self.tweet_size:
                    tweets[tweet_index] += self.hashtags
                tweet_index += 1
            #Else add sentence to existing tweet 
            else:
                tweets[tweet_index] += sentences[sentence_index]+self.appendage
                sentence_index += 1
        if (self.hashtags!=""):
            tweets.append(self.hashtags)
        return tweets

    def postTweets(self, tweet_id,tweets):
        for tweet in tweets:
            try:
                status = self.api.update_status(status=tweet.encode('utf-8'), in_reply_to_status_id=tweet_id)
                tweet_id = status.id
            except tweepy.error.TweepError as e:
                print(e)
                print(tweet + "ERROR")
            except UnicodeDecodeError as e:
                print(e)
                print(tweet + "UNICODE_DECODE_ERROR")
            except UnicodeEncodeError as e:
                print(e)
                print(tweet + "UNICODE_ENCODE_ERROR")
