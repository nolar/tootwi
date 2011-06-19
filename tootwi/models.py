# coding: utf-8
"""
Models are local proxying representations of remote Twitter data. They form
a hierarchy of classes, which looks chaotic at a first glance, but obeys few
basic principles described below. This module provides predefined models for
almost all Twitter API functionality. Developers can inherit and extend them
if necessary, or build new models easily if they are not already here. Also,
developers still can use API directly without models at all, i.e. with raw
data requests and streams; models are optional extension for the library.


= UNDERSTANDING MODELS =

There are two kind of models: item models for single entity and list models
for multiple entities if the same kind. Item models provide access to its
values in dict-like syntax (item['field']). List models provide access to its
items in list-like syntax (i.e., by iterating over it or accessing by index).

All models accept API instance as a first parameter to the constructor, and
it is required; all models are linked to the API instance so they can perform
data requests transparently. When one model instantiates another, it links
produced model to the same API instance as it belongs to.


= INSTANTIATING MODELS =

!!!

= USING MODELS =

Models are instantiated in two ways:
* As a parametrized model, which is lazy-loaded loaded on first data acess.
* As a model with the data already loaded (second constructor argument).
Former way is usually used by developers directly in the code or indirectly when
calling data retrieval methods. The latter way is usually usued internally when 
API request returns embedded data (for example, last status when fetching a user),
and those data are provided as a subfield of main model.

There are also two ways to produce the same model:

* By asking parent model to fetch its dependent data and return them as model:
    timeline = user.get_timelime() # implies filtering by user id
    for status in timeline: print(status['text'])

* By direct instance creation, provided that you have all the parameters:
    timeline = UserTimeline(api, user_id=user['user_id'])
    for status in timeline: print(status['text'])

= EXTENDING MODELS =

By using the latter way you can inherit from base model classes and use your own ones.
Overriding a class of an item in a list is easy too; you still have to make your own
API request, but the syntax is almost always the same -- see the code itself for samples.

Since all models -- items and lists -- designed to be lazy-loaded, developers
should not perform API calls, implicitly or explicitly, from constructors or when
producing dependent model. Instead, they should make only one single point where
data are loaded: load() method. If model expected to have data immediately loaded,
one should call its load() method immediatelt after instantiation. The load() method
returns the model itself, so you can chain the calls:
        return Something(self.api, ...).load()
        something = Something(api, ...).load()


= NAMING CONVENTIONS =

Class and methods names are trying to correspond to official Twitter URLs, but
adapted to library naming convention:

* All classes are CamelCased;
* All methods and arguments are lowercased and underscore_delimited;
* All methods, which produce dependent instances, are prefixes with "get_";

TODO: auto-loading of models (items! and list) when accessing data for the first time.

!!! split items, lists and stream to separate files.

!!! streams are almost like lists: a class for each source. but factory is heuristic.

??? i hope there are no list operations (insert/update/delete), only reading.

!!! concept: list _IS_ an entity. it contains other entities just like Status contains User field.

"""


class Model(object):
    """
    Base class for all data models, items and lists. Provides very basic functionality
    for descendants; more meaningful features are defined in Item and List model classes.

    Each model has a reference to the API instance. Usually this is the API instance
    that this model has came (was loaded) from. It is used to perform API calls
    when reading or modifying model's data, and to produce other derived models.

    Also, each model stores the parameters, which are passed to the constructor as kwargs
    and can be accesses as dict-keys of the model later. They are passed to API request
    when model is loaded (lazy-loaded).

    It is not a good idea to change the API instance or the model's parameters once
    the model has been created. But you can, with more or less predictable results.

    Lazy-loading and data storage (type-tolerant) facilities are provided in the base
    model class, so you can rely on them no matter whether you use items or lists.
    """

    LOAD_SOURCE = None # See Model.load() for explanation.

    #
    # Common model protocol.
    #

    def __init__(self, api, data=None, **kwargs):
        """
        Base constructor accepts all possible parameters, used or not. Descendants
        classes could specify exact parameter names in a pass-through constructors.
        These names will be used for IDE hinting when creating an instance.
        """
        super(Model, self).__init__()
        self.api = api
        self.data = data #??? rename all "data" to "values". what about lists?
        self.params = kwargs

    def __repr__(self):
        """
        Exact representation of the model, which can be used for re-creation,
        except for API instance reference, which usually hides sensitive data.
        """
        return '%s.%s(%s, %s, %s)' % (
            self.__class__.__module__,
            self.__class__.__name__,
            repr(self.api),
            repr(self.data),
            repr(self.params),
        )

    #
    # Dict-like syntax to access the model's parameters.
    #

    def __getitem__(self, name):
        return self.params[name]

    def __setitem__(self, name, value):
        self.params[name] = value

    def __delitem__(self, name):
        del self.params[name]

    def __contains__(self, name):
        return name in self.params

    #
    # Common model behavior (items and lists).
    #

    def load(self):
        """
        Loads model's data and stores them in model. Usually the schema is
        the same for all item and list models: one single source of information
        and parameters from the constructor. Descendants must specify class
        field named "LOAD_SOURCE" (tuple of http method and url). If they
        do not specify this field, NotImplemented exception will be raised
        as if the method were not implemented at all.

        If this method is overridden, it MUST return self for proper loading
        of models when derived from other models. Otherwise chained single-line
        expressions (usually derived models) will break.
        """
        if self.LOAD_SOURCE is None:
            raise NotImplemented()
        #!!! exceptions
        self.data = self.api.call(self.LOAD_SOURCE, self.params)
        return self


class Item(Model):
    """
    Base class for all single-item data models. Treats data storage, provided
    by base model class, as dict. Thus, merges paramaters and data values,
    with data values having priority over the parameters.

    TODO: solve the mess with params+data, and probably make params unmutable, or whatever else.
    """
    
    def __init__(self, api, data=None, **kwargs):
        data = dict(data) if data is not None else {}
        super(Item, self).__init__(api=api, data=data, **kwargs)
    
    #
    # Dict-like syntax for item data values. Falls back to parameters when no value is found.
    #

    #TODO: implicitly load the data if not loaded yet when accessing unknown field.

    def __getitem__(self, name):
        if name in self.data:
            return self.data[name]
        else:
            return super(Item, self).__getitem__(name)

    def __setitem__(self, name, value):
        self.data[name] = value

    def __delitem__(self, name, value):
        del self.data[name] # !!! del from params also, but handle excptions properly

    def __contains__(self, name):
        return name in self.__data or super(Item, self).__contains__(name)


class List(Model):
    """
    Base class for all multi-item data models. Treats data storage, provided
    by base model class, as list. Thus, paramaters are not in direct conflict
    with the data, but list support indexes access to the list through the same
    methods.

    Also, provides iteration over the data. Instantiation of items is performed
    when iterating rather than when setting the data (for speed and memory purposes).
    Item class (or any other factory-like function) must be specified in ITEM_CLASS
    class field; if it is a model class, then API instance will be pased to it.

??? Implicitly loads the data on first access. For this, each descendant
??? model class should specify class fields as follows:
??? * ITEM_CLASS must point to the class of the items.
    """

    ITEM_CLASS = None # See List.make_item() for details.

    def __iter__(self):
        self.load()#??? autoloading is under question
        for item in self.data:
            yield self.make_item(item)

    def make_item(self, data):
        """
        Item factory. The result of this function will be yielded when iterating
        over the list. By default, it depends on ITEM_CLASS field, which is usually
        defined in descendant classes. If this class points to a model, the API
        instance will be passed to it; otherwise, the instance is created normally.
        """
        if self.ITEM_CLASS is None:
            raise NotImplemented()
        elif issubclass(self.ITEM_CLASS, Model):
            return self.ITEM_CLASS(self.api, data)
        else:
            return self.ITEM_CLASS(data)


class Account(Item):
    """
    Account is an extra entity, which is semantically linked one-to-one with current
    API credentials, since account is an extended functionality for currently authorized
    user, with no need to specify the user directly. When you need to work with currently
    authorized user as one of all ther users, you need to verify credentials and fetch
    the AccountUser instance.
    """

    def verify_credentials(self):
        return AccountUser(self.api).load()

#!!! move to their own classes
#   RATE_LIMIT_STATUS  = ('GET', 'account/rate_limit_status')
#   TOTALS = ('GET', 'account/totals')
#   GET_SETTINGS = ('GET' , 'account/settings')
#   SET_SETTINGS = ('POST', 'account/settings')
#   UPDATE_PROFILE = account/update_profile
#   UPDATE_PROFILE_COLORS = account/update_profile_colors
#   UPDATE_PROFILE_IMAGE = account/update_profile_image
#   UPDATE_PROFILE_BACKGROUND_IMAGE = account/update_profile_background_image
#
#   def rate_limit_status(self):
#       #!!! make special class for rate limits, with its own structure
#       return self.api.call(self.RATE_LIMIT_STATUS, dict(...))
#
#   def totals(self):
#       #!!! make special class for totals, with its own structure
#       return self.api.call(self.TOTALS, dict(...))
# 
#   def get_settings(self):
#       #!!! make special model entity for settings, with its own structure and load()/save() methods
#       return self.api.call(self.GET_SETTINGS)
# 
#   def set_settings(self, ...):
#       return self.api.call(self.SET_SETTINGS, dict(...))
#
#   def update_profile(self):
#       self.api.call(self.UPDATE_PROFILE, dict(...))
#
#   def update_profile_colors(self):
#       self.api.call(self.UPDATE_PROFILE_COLORS, dict(...))
#
    def get_public_timeline(self):# this is inside an account for proper rate limiting/throttling
        return PublicTimeline(self.api).load()


class User(Item):
    """
    User is regular user entity. It represents currently euthenticated user and all other
    users in Twitter.
    """

    LOAD_SOURCE = ('GET', 'users/show')
    PROFILE_IMAGE = ('GET', 'users/profile_image/%(screen_name)s')

    # Pass-through constructor for IDE auto hinting.
    def __init__(self, api, data=None, user_id=None, screen_name=None, include_entities=None, skip_status=None):
        super(User, self).__init__(api, data, user_id=user_id, screen_name=screen_name, include_entities=include_entities, skip_status=skip_status)

#   def profile_image(self):
#       #!!! this is Http 302 redirect rather than request output - catch and return new url
#       self.api.call(self.PROFILE_IMAGE, dict(screen_name=self['screen_name']))

    def contributors(self):
        return Contributors(self.api, user_id=self['id']).load()

    def contributees(self):
        return Contributees(self.api, user_id=self['id']).load()


class AccountUser(User):
    LOAD_SOURCE = ('GET', 'account/verify_credentials')

    # Pass-through constructor for IDE auto hinting.
    def __init__(self, api, data=None, include_entities=None, skip_status=None):
        super(AccountUser, self).__init__(api, data, include_entities=include_entities, skip_status=skip_status)

#!!!    
## produced from Account -- Account().suggestions() -- since it is account-dependant.
#class Suggestions(List):
##  SUGGESTIONS = ('GET', 'users/suggestions')
#   # iterates over Suggestion
#   ITEM_CLASS = Suggestion

#!!!
#class Suggestion(Item):
#   # represents a category slug.
#   def users(self):
#       return Users(self.api.call(self.SUGGESTION_SLUG, dict(slug=...)))


#!!! move to special classes and methods
#class Users(List):
#   LOOKUP = ('GET', 'users/lookup')
#   SEARCH = ('GET', 'users/search')
#   SUGGESTIONS = ('GET', 'users/suggestions')
#   SUGGESTIONS_TWITTER = ('GET', 'users/suggestions/%(slug)s')


class Status(Item):
    LOAD_SOURCE = ('GET', 'statuses/show/%(id)s')
    UPDATE  = ('POST', 'statuses/update')
    RETWEET = ('POST', 'statuses/retweet/%(id)s')
    DESTROY = ('POST', 'statuses/destroy/%(id)s')

#   # Pass-through constructor for IDE auto hinting.
#   def __init__(self, api, params=None, id=None, text=None):#!!! add more of them
#       super(Status, self).__init__(api, params, id=id, text=text)

    def update(self):
        self.data = self.api.call(self.UPDATE, dict(status=self['text']))#!!! more args

    def retweet(self):
        return Status(self.api, self.api.call(self.RETWEET, dict(id=self['id'])))

    def destroy(self):
        self.api.call(self.DESTROY, dict(id=self['id']))
        del self.data

    def get_user(self):
        return User(self.api, self['user'])

    def get_retweets(self):
        return Retweets(self.api, id=self['id']).load()

    def get_retweeted_by(self):
        return RetweetedBy(self.api, id=self['id']).load()

    def get_retweeted_by_ids(self):
        return RetweetedByIds(self.api, id=self['id']).load()
        #??? we what just a list[int/str], no need for a wrapper class.


class Users(List):
    ITEM_CLASS = User

class Contributors(Users):
    LOAD_SOURCE = ('GET', 'users/contributors')

class Contributees(Users):
    LOAD_SOURCE = ('GET', 'users/contributees')

class RetweetedBy(Users):
    LOAD_SOURCE = ('GET', 'statuses/%(id)s/retweeted_by')

class RetweetedByIds(List):
    ITEM_CLASS = int
    LOAD_SOURCE = ('GET', 'statuses/%(id)s/retweeted_by/ids')

class Statuses(List):
    ITEM_CLASS = Status

class Retweets(Statuses):
    LOAD_SOURCE = ('GET', 'statuses/retweets/%(id)s')

class PublicTimeline(Statuses):
    LOAD_SOURCE = ('GET', 'statuses/public_timeline')

