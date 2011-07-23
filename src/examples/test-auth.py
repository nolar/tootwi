#!/usr/bin/env python
import settings # must have! it contains sys.path adjustments.
import datetime
from tootwi import ApplicationCredentials

def main():
    
    #
    # Stage 1 of 3: make request and gain temporary credentials.
    #
    application_credentials = ApplicationCredentials(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    temporary_credentials = application_credentials.request()
    
    #
    # Stage 2 of 3: forward user to authorization page and retrieve pin code (or callback).
    #
    print(temporary_credentials.url)
    pin = raw_input('pin: ')
    
    #
    # Stage 3 of 3: gain access credentials with pin code or callback verifier.
    #
    token_credentials = temporary_credentials.confirm(pin)
    
    #
    # Last check: try to use access credentials (not a part of authorization already).
    #
    user = token_credentials.account.verify_credentials()
    print(user)
    

if __name__ == '__main__':
    main()
