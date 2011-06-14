import unittest
from . import API

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCOUNT_TOKEN_KEY = ''
ACCOUNT_TOKEN_SECRET = ''

class APITest(unittest.TestCase):
	def testAnonymousCReated(self):
		api = Anonymous()
#		timeline = api.getPublicTimelime()
#		self.assertTrue(len(timelime) > 0, msg="Public timeline is empty -- quite unbelievable.")

	def testApplicationCreationUnattachedDirectly(self):
		api = Application(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)

	def testApplicationCreationFromAnonymousDirectly(self):
		Application(Anonymous(), consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)

	def testApplicationCreationFromAnonymousViaFactory(self):
		Anonymous().createApplication(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)

	def testApplicationCreationFailsFromApplication(self):#???
		source = Application(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)
#		with self.assertRaises(???):
#			Application(source, consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)

	def testApplicationCreationFailsFromAccount(self):#???
		source = Application(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)
#		with self.assertRaises(???):
#			Application(source, consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)

	def testApplicationCreationFailsWithoutConsumer(self):
		with self.assertRaises(ApplicationConsumerAbsentError):
			api = Application()

	def testApplicationCreationFailsWithoutConsumerKey(self):
		with self.assertRaises(ApplicationConsumerAbsentError):
			api = Application(consumer_key=CONSUMER_KEY)

	def testApplicationCreationFailsWithoutConsumerSecret(self):
		with self.assertRaises(ApplicationConsumerAbsentError):
			api = Application(consumer_secret=CONSUMER_SECRET)


	def testAccountCreatedDirecty(self):
		api = Account(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET,
				token_key=ACCOUNT_TOKEN_KEY, token_secret=ACCOUNT_TOKEN_SECRET)

	def testAccountCreatedWithApplication(self):
		app = Application(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)
		api = Account(app, token_key=ACCOUNT_TOKEN_KEY, token_secret=ACCOUNT_TOKEN_SECRET)



if __name__ == '__main__':
	unittest.main()
