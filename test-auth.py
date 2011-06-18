import datetime
from tootwi import API
from tootwi.models import Status, User, PublicTimeline, Account
from tootwi.throttlers import TimedThrottler, LatestGroupThrottler, SoonestGroupThrottler
from tootwi.credentials import OAuthCredentials, OAuthConsumerCredentials, OAuthAccessCredentials, OAuthRequestCredentials
from tootwi.connections import urllib2Connection
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

def main():
    connection = urllib2Connection()
    credentials = OAuthConsumerCredentials(
                    CONSUMER_KEY, CONSUMER_SECRET)
    api = API(credentials, connection)
    
    r = api.request()
    print(r)
    
    print
    print(r[0])
    pin = raw_input('pin: ')
    
    credentials = OAuthRequestCredentials(
                    CONSUMER_KEY, CONSUMER_SECRET,
                    r[1], r[2])
    api = API(credentials, connection)
    
    v = api.verify(pin)
    print(v)
    
    

if __name__ == '__main__':
    main()
