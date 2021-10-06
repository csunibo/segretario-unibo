from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pyrogram import filters
from apscheduler.schedulers.background import BackgroundScheduler


from lectures import getCourse, get_lectures
from message import Message
from mongo import getClient, getRemoteClient
from lookForGroups import LookForGroups

class Bot():
	# REGION INIT
	def __init__(self):
		"""
		Constructor: gets by default config.ini files on project root
		"""
		self.client = Client("segretario_log")

		self.scheduler = BackgroundScheduler()
		self.scheduler.add_job(self.update_every_day, "interval", seconds=10)
		self.mongo = getClient()
		self.Group = LookForGroups()

		self.actions = list(self.mongo.actions.find({}))
		command_filters = []
		for action in self.actions:
			command_filters.append(action["command"])

		self.client.add_handler(MessageHandler(self.__act, filters.command(command_filters)))

	def update_every_day(self):
		self.client.send_message(0, "test")

	def __act(self, client, message):
		# TODO: questo switch è diventato troppo lungo, bisogna refactorare
		# dividendolo in passi molto più semplici
		commandName = message.command[0]
		action = self.mongo.actions.find_one({"command": commandName})
		_type = action["type"]
		if _type == 'course':
			res = getCourse(message, action)
			self.send_message(res)
		elif _type == 'todayLesson':
			action['dati']['isTomorrow'] = False
			msg = Message(message, data=action['dati'])
			res = get_lectures(msg)
			self.send_message(res)
		elif _type == 'tomorrowLesson':
			action['dati']['isTomorrow'] = True
			msg = Message(message, data=action['dati'])
			res = get_lectures(msg)
			self.send_message(res)
		elif _type == 'help':
			self.get_help(message)
		elif _type == 'message':
			msg = Message(message, text=action['dati']['text'])
			self.send_message(msg)
		elif _type == 'lookingFor':
			msg = Message(message)
			res = self.Group.add(msg)
			msg = self.getChatMember(res)
			self.send_message(msg)
		elif _type == 'notLookingFor':
			msg = Message(message)
			res = self.Group.remove(msg)
			self.send_message(res)
		else:
			raise TypeError(f"Unknown action type {_type}")
	# ENDREGION

	def send_message(self, messageClass: Message):
		self.client.send_message(messageClass.chat.id, text=messageClass.text)

	# REGION GIVE HELP
	def get_help(self, message):
		answer = ""
		courses = ""
		for command in self.actions:
			if command['type'] == "course":
				courses += f"/{command['command']}\n"
				continue
			
			if (command['description']['is_present'] == False):
				continue

			answer += f"/{command['command']}: {command['description']['text']}\n"

		answer += "\n<b>I corsi attivi: </b>\n"
		answer += courses
		messageStruct = Message(message, text=answer)
		print(messageStruct)
		self.send_message(messageStruct)
	# ENDREGION

	# REGION LOOKING GROUPS
	def getChatMember(self, message: Message) -> Message:
		# TODO: the checks should be on the database, not here
		# security check first of all :D, just trying to control the flow
		num_docs = self.mongo.lookgroups.count_documents({"chatId": message.chat.id})
		if num_docs > 1:
			raise Exception("Detected two copies of the same chat in the database")

		chat_members = self.mongo.lookgroups.find_one({"chatId": message.chat.id})['senderIds']

		answer = ""
		for senderId in chat_members:
			user = self.client.get_chat_member(message.chat.id, senderId)['user']
			answer += f"\n👤 <a href='tg://user?id={user.id}'>{user.first_name}{' ' + user.last_name if user.last_name else ''}</a>"
		
		message.text += answer
		return message