import datetime
from tootwi import API
from tootwi.models import Status, User, PublicTimeline, Account
from tootwi.streams import SampleStream, FilterStream, MessageFactory
from tootwi.throttlers import TimedThrottler, LatestGroupThrottler, SoonestGroupThrottler
from tootwi.credentials import OAuthCredentials, OAuthConsumerCredentials, OAuthAccessCredentials
from tootwi.connections import urllib2Connection

def main():
    connection = urllib2Connection()
    credentials = OAuthAccessCredentials(#OAuthConsumerCredentials(
            'vvp8yXv5zus4gttWflFWCA', '40ehdqH7BFgyvYwUvEAd5Guxj8eISYqOTMkiV5jwE',
            '313826855-5gn5dNTNgjPyQRRGEmBFMVSKtMBh41CcyHVkcK0J','tu4ZV6xCKtbttiz01loY5Byp34KjOjbBsnG4WeOg')
    api = API(credentials, connection)

#   stream = FilterStream(api, MessageFactory(), follow=[16132160,313826855])
    stream = SampleStream(api, MessageFactory())
    for item in stream:
        print(item)
        exit()

if __name__ == '__main__':
    main()
