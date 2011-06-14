# coding: utf-8
"""
Throttlers are responsible for limiting the number of requests per second.
They are optionally passed to the constructor of the API instances.

Since Twitter limits are complicated (there are user limits, host limits, feature
limits, etc; and some requests have no limits), it is up to the application on how
to throttle, and whether to throttle at all.

The concept is this: a throttler can calculate what time the application should
wait before performing its next request. What logic the throttler uses is up to it.
Every request "touches" the associated throttler, so it should update its state.
The throttler can also be reset, so as if just created.

Group throttlers allow to build complex throttling logic with simple blocks.
"Soonest" group allows to perform the request once at least one of its throttlers
is ready; "Latest" group waits till all of its throttlers are ready. Throttlers
can be used in "&" and "|" bitwise operators to build the groups:
	throttler1 & throttler2 & throttler2 -- gives us "latest" group.
	throttler1 | throttler2 | throttler2 -- gives us "soonest" group.
More complex formulas can be used if needed. Original throttlers are not modified
and still can be used on their own, while being in one or more groups.
"""

import time
import datetime


class Throttler(object):
	"""
	Base throttler. Should never be instantiated directly.
	Provides basic throttler behavior (such as grouping)
	and a protocol for descendants to implement.
	"""

	def __and__(self, other):
		return LatestGroupThrottler([self, other])

	def __or__(self, other):
		return SoonestGroupThrottler([self, other])

	def wait(self):
		to_wait = self.check()
		time.sleep(to_wait) # assuming that it is never negative and that zero time has no impact
		self.touch()

	def check(self):
		raise NotImplemented()

	def touch(self):
		raise NotImplemented()

	def reset(self):
		raise NotImplemented()


class GroupThrottler(Throttler):
	"""
	Base group throttler. Group consists of other throttlers, which are
	touched and reset alltogether. Specific calculations for a time to wait
	are implemented in descendant group classes.
	"""

	def __init__(self, throttlers):
		super(GroupThrottler, self).__init__()
		self.throttlers = list(throttlers) # force all kind of iterables to the list

	def touch(self):
		for throttler in self.throttlers:
			throttler.touch()

	def reset(self):
		for throttler in self.throttlers:
			throttler.reset()


class LatestGroupThrottler(GroupThrottler):
	"""
	Group throttler, which allows to perform a request when all of its member throttlers are ready.
	"""

	def check(self):
		return max([throttler.check() for throttler in self.throttlers])

	def __and__(self, other):
		"""
		Optimize initial operation to produce only one single group rather
		than a tree, when few throttlers are joined (th1 & th2 & th3).
		"""
		if isinstance(other, LatestGroupThrottler):
			return LatestGroupThrottler(self.throttlers + other.throttlers)
		return LatestGroupThrottler(self.throttlers + [other])


class SoonestGroupThrottler(GroupThrottler):
	"""
	Group throttler, which allows to perform a request when at least one of its member throttlers is ready.
	"""

	def check(self):
		return min([throttler.check() for throttler in self.throttlers])

	def __or__(self, other):
		"""
		Optimize initial operation to produce only one single group rather
		than a tree, when few throttlers are joined (th1 | th2 | th3).
		"""
		if isinstance(other, SoonestGroupThrottler):
			return SoonestGroupThrottler(self.throttlers + other.throttlers)
		return SoonestGroupThrottler(self.throttlers + [other])


class TimedThrottler(Throttler):
	"""
	Sample throttler, which limits the number of requests per second
	regardless of the time of the requests and any other states and stats.
	"""

	def __init__(self, requests_per_second):
		super(TimedThrottler, self).__init__()
		self.requests_per_second = requests_per_second
		self.seconds_per_request = 1. / requests_per_second
		self.last = None

	def check(self):
		ts = datetime.datetime.now()
		if self.last is not None:
			elapsed = ts - self.last
			elapsed = elapsed.seconds + elapsed.microseconds / 1000000.
			to_wait = max(0.0, self.seconds_per_request - elapsed) # max() is to catch negative deltas
			return to_wait
		else:
			return 0.0
		
	def touch(self):
		self.last = datetime.datetime.now()

	def reset(self):
		self.last = None


class AccountThrottler(Throttler):
	pass#!!!


class FeatureThrottler(Throttler):
	pass#!!!

