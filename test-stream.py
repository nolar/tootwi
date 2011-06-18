import datetime
from tootwi import API
from tootwi.streams import SampleStream, FilterStream, MessageFactory
from tootwi.credentials import OAuthConsumerCredentials, OAuthAccessCredentials
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

def main():
    credentials = OAuthAccessCredentials(#OAuthConsumerCredentials(
                    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    api = API(credentials)

#   stream = FilterStream(api, MessageFactory(), follow=[16132160,313826855])
    stream = SampleStream(api, MessageFactory())
    for item in stream:
        print(item)
        exit()

if __name__ == '__main__':
    main()
