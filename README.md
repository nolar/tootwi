# ABOUT

TooTwi is a python library for Twitter API, intended to be truly object-oriented,
extendible and fast, yet supporting all Twitter API methods, current and future.

# FEATURES

* Streams iterators.
* OAuth and basic auth support (still allowed in streams).
* A lot of properly designed data models with mutual relations.
* Easyness of inheritance and enhancement.


# CODE SAMPLES

Working code samples are in test-auth.py, test-models.py, and test-stream.py.

## Three-stage Twitter OAuth PIN authentication:

```python
    from tootwi import ApplicationCredentials
    from settings import CONSUMER_KEY, CONSUMER_SECRET

    # Stage 1 of 3: make request and gain temporary credentials.
    application_credentials = ApplicationCredentials(CONSUMER_KEY, CONSUMER_SECRET)
    temporary_credentials = application_credentials.request()

    # Stage 2 of 3: forward user to authorization page and retrieve pin code (or callback).
    print('Enter PIN from %s' % temporary_credentials.url)
    pin = raw_input('PIN: ')

    # Stage 3 of 3: gain access credentials with pin code or callback verifier.
    token_credentials = temporary_credentials.confirm(pin)

    # Last check: try to use access credentials (not a part of authorization already).
    user = token_credentials.account.verify_credentials()
    print(user)
```


## Models:

```python
    from tootwi import TokenCredentials
    from tootwi.models import Status, User, PublicTimeline, Account
    from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

    credentials = TokenCredentials(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)

    user = Account(credentials).verify_credentials()
    print(user)

    timeline = PublicTimeline(credentials)
    print(timeline[0])
    for status in timeline: print(status)

    Status(credentials, text='hello world at %s' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).update()
    Status(credentials, text='bye world at %s'   % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).update()
```


## Streams:

```python
    from tootwi import TokenCredentials
    from tootwi.streams import SampleStream, FilterStream, MessageFactory
    from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

    credentials = TokenCredentials(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)

    for item in FilterStream(credentials, MessageFactory(), follow=[16132160,313826855]):
        print(item)

    for item in SampleStream(credentials, MessageFactory()):
        print(item)
```



# HISTORY AND STATUS

This library is a byproduct of a few experiments with Twitter API and streams.
There is a library with even more features and API coverage: "tweepy" (http://tweepy.github.com/).
At the moment of the experiments it has been moving to another repository, thus poorly searchable.
And it is still completely not documented unless you read its code. No wonder why I've missed it.

This tootwi project is under development now, new fatures are added constantly.
The concept and the names of the classes are altered time to time, but will be fixed soon.

