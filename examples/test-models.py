import datetime
from tootwi import TokenCredentials
from tootwi.models import Status, User, PublicTimeline, Account
from tootwi.throttlers import TimedThrottler
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

def main():
    credentials = TokenCredentials(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    #throttler = SoonestGroupThrottler([TimedThrottler(.1), TimedThrottler(.2)])

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

    user = Account(credentials).verify_credentials()
    print(user)

    timeline = PublicTimeline(credentials)
    print(timeline[0])
    print
    print(timeline[-1:])
    print

    Status(credentials, text='hello world at %s' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).update()
    Status(credentials, text='bye world at %s' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).update()

if __name__ == '__main__':
    main()
