import datetime
from tootwi import API
from tootwi.models import Status, User, PublicTimeline, Account
from tootwi.streams import SampleStream, FilterStream, MessageFactory
from tootwi.throttlers import TimedThrottler, LatestGroupThrottler, SoonestGroupThrottler
from tootwi.credentials import OAuthCredentials, OAuthConsumerCredentials, OAuthAccessCredentials
from tootwi.connections import urllib2Connection
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

def main():
    connection = urllib2Connection()
    credentials = OAuthAccessCredentials(#OAuthConsumerCredentials(
                    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    api = API(credentials, connection)

#   stream = FilterStream(api, MessageFactory(), follow=[16132160,313826855])
    stream = SampleStream(api, MessageFactory())
    for item in stream:
        print(item)
        exit()

if __name__ == '__main__':
    main()
