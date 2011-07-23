# coding: utf-8

class Stream(object):
    OPEN_OPERATION = None
    
    def __init__(self, api, factory=None, **kwargs):
        super(Stream, self).__init__()
        self.api = api
        self.factory = factory
        self.params = kwargs

    def __iter__(self):
        for data in self.api.flow(self.OPEN_OPERATION, self.params):
            item = self.factory(self.api, data) if self.factory is not None else data
            if item is not None:
                yield item

    def make_item(self, data):
        """
        Item factory. The result of this function will be yielded when iterating
        over the list. By default, it depends on ITEM_CLASS field, which is usually
        defined in descendant classes. If this class points to a model, the API
        instance will be passed to it; otherwise, the instance is created normally.
        """
        return 


class SampleStream(Stream):
    OPEN_OPERATION = ('GET' , 'http://stream.twitter.com/1/statuses/sample')
    def __init__(self, api, factory=None):
        super(SampleStream, self).__init__(api, factory)

class FilterStream(Stream):
    OPEN_OPERATION = ('POST', 'http://stream.twitter.com/1/statuses/filter')
    def __init__(self, api, factory=None, follow=None):
        if not isinstance(follow, basestring):
            follow = list(follow) if follow is not None else []
            follow = ','.join([unicode(v) for v in follow])
        super(FilterStream, self).__init__(api, factory, follow=follow)

class FirehoseStream(Stream):
    OPEN_OPERATION = ('GET' , 'http://stream.twitter.com/1/statuses/firehose')
    def __init__(self, api, factory=None):
        super(FirehoseStream, self).__init__(api, factory)

class LinksStream(Stream):
    OPEN_OPERATION = ('GET' , 'http://stream.twitter.com/1/statuses/links')
    def __init__(self, api, factory=None):
        super(LinksStream, self).__init__(api, factory)

class RetweetStream(Stream):
    OPEN_OPERATION = ('GET' , 'http://stream.twitter.com/1/statuses/retweet')
    def __init__(self, api, factory=None):
        super(RetweetStream, self).__init__(api, factory)

class UserStream(Stream):
    OPEN_OPERATION = ('POST', 'https://userstream.twitter.com/2/user')
    def __init__(self, api, factory=None):
        super(UserStream, self).__init__(api, factory)



#!!! it is not good that factory is here. it is not used usually, and its logic can vary.
#!!! but we are lazy to import each message class in separate module :-)
from .models import Item, Status
class MessageFactory(object):
    def __call__(self, api, data):
        """
        Attempts to recognize the message by its data and instantiate it as of appropriate class.
        Specific classes are useful for quick-checks with isinstance(); also they extend the message
        with additional behavior and field handling.

        Recognition logic can be not precise and produce instances of improper classes.
        Developers are free to use their own logic for instantiation. This one is library's default.
        Factory instances are passed to streams and requests when they are being constructed.
        """
        if data is None:
            return None # will be ignored by API.flow()
        #elif 'friends' in data: # guess if this is a friend list
        #   return Friends(data)
        elif 'text' in data: # guess if this is a new status update
            return Status(api, data)
        else:
            return Unknown(api, data)

class Unknown(Item):
    """
    Used in factory for messages, which can not be recognized to their specific classes.
    Developers can still access all data and fields as usually with no additionla features.
    The reason not to use Message class itself is to make such a messages easy recognizable
    with isinstance(), so if instantiated as Message then recognized messages will fit too.
    """
    pass
