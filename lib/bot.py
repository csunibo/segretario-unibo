from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pyrogram import filters
from apscheduler.schedulers.background import BackgroundScheduler
import json


from lectures import getCourse, get_lectures
from mongo import getClient, getRemoteClient
from lookForGroups import LookForGroups

class Bot():
	# REGION INIT
	def __init__(self):
		"""
		Constructor: gets by default config.ini files on project root
		"""
		self.client = Client(
			"segretario_log"
		)

		self.scheduler = BackgroundScheduler()
		self.scheduler.add_job(self.update_every_day, "interval", seconds=10)
		self.mongo = getRemoteClient()
		self.Group = LookForGroups()

		self.actions = list(self.mongo.actions.find({}))

		for action in self.actions:
			self.client.add_handler(MessageHandler(self.__act, filters.command(action["type"])))

	def update_every_day(self):
		self.client.send_message(457951837, "test")

	def __act(self, client, message):
		_type = message.command[0]
		if _type == 'course':
			getCourse(message.chat.id, action)
		elif _type == 'todayLesson':
			get_lectures(self.client, message.chat.id, action, isTomorrow=False)
		elif _type == 'tomorrowLesson':
			get_lectures(self.client, message.chat.id, action, isTomorrow=True)
		elif _type == 'help':
			self.get_help(message)
		elif _type == 'message':
			self.client.send_message(message.chat.id, action['text'])
		elif _type == 'lookingFor':
			res = self.Group.add(message)
			self.handleResponse(action, res, message.chat.title)
		elif _type == 'notLookingFor':
			res = self.Group.remove(message)
			self.handleResponse(action, res, message.chat.title)
		elif _type == "toggleSleep":
			Sleep.toggle(message)
		else:
			raise TypeError(f"Unknown action type {type}")
	# ENDREGION

	# REGION GIVE HELP
	def get_help(self, message):
		answer = ""
		courses = ""
		for command in self.actions:
			if command['type'] == "course":
				courses += f"/{command['command']}\n"
				continue
			try:
				answer += f"/{command['command']}: {command['description']}\n"
			except Exception as e:
				print(e)
				continue
			#aggiungere le descrizione per togliere il try catch
		answer += "\n<b>I corsi attivi: </b>\n"
		answer += courses
		self.client.send_message(message.chat.id, answer)
	# ENDREGION

	# REGION LOOKING GROUPS
	def handleResponse(self, action, res, title):
		if res['status'] == 403:
			try:
				self.client.send_message(res['chatId'], action['chatError'])
			except KeyError:
				print("Malformed JSON, there is no chatError key in the object")
			return
		elif res['status'] == 404:
			try:
				print(type(action['notFoundError']))
				print(action['notFoundError'])
				self.client.send_message(res['chatId'], action['notFoundError'].format(title))
			except KeyError:
				print("Malformed JSON, there is no notFoundError key in the object")
			return

		if res['remove']:
			self.client.send_message(res['chatId'], action['text'].format(title))
		else:
			title = action['text'].format(title)
			lookers = self.getChatMember(res['chatId'])
			self.client.send_message(res['chatId'], title + lookers)

	def getChatMember(self, chatId):
		# security check first of all :D, just trying to control the flow
		num_docs = self.mongo.lookgroups.count_documents({"chatId": chatId})
		if num_docs > 1:
			raise Exception("Detected two copies of the same chat in the database")

		chat_members = self.mongo.lookgroups.find_one({"chatId": chatId})['senderIds']

		answer = ""
		for senderId in chat_members:
			user = self.client.get_chat_member(chatId, senderId)['user']
			answer += f"\n👤 <a href='tg://user?id={user.id}'>{user.first_name}{' ' + user.last_name if user.last_name else ''}</a>"
		
		return answer