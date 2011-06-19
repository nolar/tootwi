import datetime
from tootwi import TokenCredentials
from tootwi.streams import SampleStream, FilterStream, MessageFactory
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

def main():
    credentials = TokenCredentials(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)

#   stream = FilterStream(credentials, MessageFactory(), follow=[16132160,313826855])
    stream = SampleStream(credentials, MessageFactory())
    for item in stream:
        print(item)
        exit()

if __name__ == '__main__':
    main()
