import datetime
from tootwi import API
from tootwi.models import Account
from tootwi.credentials import OAuthConsumerCredentials, OAuthAccessCredentials, OAuthRequestCredentials
from settings import CONSUMER_KEY, CONSUMER_SECRET

def main():
    
    #
    # Stage 1 of 3: make request and gain temporary credentials.
    #
    credentials = OAuthConsumerCredentials(
                    CONSUMER_KEY, CONSUMER_SECRET)
    api = API(credentials)
    r = api.request()
    print(r)
    
    #
    # Stage 2 of 3: forward user to authorization page and retrieve pin code (or callback).
    #
    print
    print(r[0])
    pin = raw_input('pin: ')
    
    #
    # Stage 3 of 3: gain access credentials with pin code or callback verifier.
    #
    credentials = OAuthRequestCredentials(
                    CONSUMER_KEY, CONSUMER_SECRET,
                    r[1], r[2])
    api = API(credentials)
    v = api.verify(pin)
    print(v)
    
    #
    # Last check: try to use access credentials (not a part of authorization already).
    #
    credentials = OAuthAccessCredentials(
                    CONSUMER_KEY, CONSUMER_SECRET,
                    v[0], v[1])
    api = API(credentials)
    u = Account(api).verify_credentials()
    print(u)
    

if __name__ == '__main__':
    main()
