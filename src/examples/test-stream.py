#!/usr/bin/env python
import settings # must have! it contains sys.path adjustments.
import datetime
from tootwi import TokenCredentials
from tootwi.streams import SampleStream, FilterStream, MessageFactory

def main():
    credentials = TokenCredentials(settings.CONSUMER_KEY, settings.CONSUMER_SECRET, settings.ACCESS_KEY, settings.ACCESS_SECRET)

#   stream = FilterStream(credentials, MessageFactory(), follow=[16132160,313826855])
    stream = SampleStream(credentials, MessageFactory())
    for item in stream:
        print(item)
        exit()

if __name__ == '__main__':
    main()
