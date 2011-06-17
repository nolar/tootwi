import datetime
from tootwi import API
from tootwi.models import Status, User, PublicTimeline, Account
from tootwi.throttlers import TimedThrottler, LatestGroupThrottler, SoonestGroupThrottler
from tootwi.credentials import OAuthCredentials, OAuthConsumerCredentials, OAuthAccessCredentials
from tootwi.connections import urllib2Connection

def main():
    connection = urllib2Connection()
    credentials = OAuthAccessCredentials(#OAuthConsumerCredentials(
            'vvp8yXv5zus4gttWflFWCA', '40ehdqH7BFgyvYwUvEAd5Guxj8eISYqOTMkiV5jwE',
            '313826855-5gn5dNTNgjPyQRRGEmBFMVSKtMBh41CcyHVkcK0J','tu4ZV6xCKtbttiz01loY5Byp34KjOjbBsnG4WeOg')
    #throttler = SoonestGroupThrottler([TimedThrottler(.1), TimedThrottler(.2)])
    api = API(credentials, connection)

    #for item in api.flow(api.FILTER_STREAM, dict(follow='16132160,313826855')):
    #   print(item)

    # OOP way:
    #   thr = twitter.AccountThrottler(auth)
    #
    #   rq1 = twitter.PublicTimeline()
    #   #rq1.read() # optional, since inplicit on data use
    #   for item in rq1: print(item)
    #
    #   rq2 = twitter.UserInfo(auth, id, throttler=thr)
    #   rq2.id, rq.screen_name, rq['friends'], etc  -- implicit read
    #
    #   thr.refresh()  -- reloads the stats from API (for AccountThrottlers only)
    #
    # I.e., oop way is _proxying_ rather than lots of read/request methods (god object).
    # Throttlers make methods to blockingly wait before real request is made.

    u = Account(api).verify_credentials()
    print(u)

    timeline = PublicTimeline(api)
    print(list(timeline)[0]) # implies one-time read()

    #verify = VerifyCredentials(credentials, throttler=throttler)
    #print(verify.user) #implies one-time read()

    #Status(api, text='hello world at %s' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).update()
    #Status(api, text='bye world at %s' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).update()

if __name__ == '__main__':
    main()
