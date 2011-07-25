## ABOUT

TooTwi is a python library for Twitter API, intended to be truly object-oriented,
extendible and fast, yet supporting all Twitter API methods, both available now
and possible in future.

## FEATURES

* Easy OAuth authorization (one line per stage).
* Basic auth support (still supported in streams).
* Streams as iterators with simple syntax.
* Data models with mutual relations.
* Easyness of inheritance and enhancement.
* Object-oriented design (not a "god" object).


## CODE SAMPLES

Here are three code samples for sneak preview.
More code samples can be found in [tree/master/examples](examples) folder.


#### Three-stage Twitter OAuth authentication:

```python
    from tootwi import ApplicationCredentials
    from settings import CONSUMER_KEY, CONSUMER_SECRET

    # Stage 1 of 3: make request and gain temporary credentials.
    application_credentials = ApplicationCredentials(CONSUMER_KEY, CONSUMER_SECRET)
    temporary_credentials = application_credentials.request()

    # Stage 2 of 3: forward user to authorization page and retrieve pin code (or callback).
    pin = raw_input('Enter PIN from %s\nPIN:' % temporary_credentials.url)

    # Stage 3 of 3: gain access credentials with pin code or callback verifier.
    token_credentials = temporary_credentials.confirm(pin)

    # Last check: try to use access credentials (not a part of authorization already).
    print(token_credentials.account.verify_credentials())
```


#### Models:

```python
    from tootwi import TokenCredentials
    from tootwi.models import Account, PublicTimeline, Status
    from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

    credentials = TokenCredentials(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)

    user = Account(credentials).verify_credentials()
    print(user)

    timeline = PublicTimeline(credentials)
    print(timeline[0])
    for status in timeline: print(status)
    
    Status(credentials, text='hello world').update()
```


#### Streams:

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



## HISTORY AND STATUS

This library is a byproduct of a few experiments with Twitter API and streams.
It is under heavy development right now (feel free to join or just watch).

If your are looking for similar projects, take a look here:

* tweepy (http://tweepy.github.com/)
