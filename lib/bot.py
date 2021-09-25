from pyrogram import Client
from pyrogram.handlers import MessageHandler
import json

from lectures import getCourse, get_lectures
from mongo import getClient
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
		self.client.add_handler(MessageHandler(self.__onMessage))
		self.mongo = getClient()
		self.Group = LookForGroups()
		
	def __onMessage(self, client, msg):
		text = str(msg['text'])
		if not text or text[0] != "/":
			return

		command = text.split(" ")[0]  
		command = text.split("@")[0][1::]

		command_count = self.mongo.actions.count_documents({"command": command})

		if command_count == 1:
			command_data = self.mongo.actions.find_one({"command": command})
			self.__act(msg, command_data)
		elif command_count > 1:
			raise Exception("Malformed JSON in MongoDB")

	def __act(self, msg, action):
		type = action['type']
		if type == 'course':
			getCourse(msg.chat.id, action)
		elif type == 'todayLesson':
			get_lectures(self.client, msg.chat.id, action, isTomorrow=False)
		elif type == 'tomorrowLesson':
			get_lectures(self.client, msg.chat.id, action, isTomorrow=True)
		elif type == 'help':
			self.giveHelp(msg.chat.id)
		elif type == 'message':
			self.client.send_message(msg.chat.id, action['text'])
		elif type == 'lookingFor':
			res = self.Group.add(msg)
			self.handleResponse(action, res, msg.chat.title)
		elif type == 'notLookingFor':
			res = self.Group.remove(msg)
			self.handleResponse(action, res, msg.chat.title)
		elif type == "toggleSleep":
			Sleep.toggle(msg)
		else:
			raise TypeError(f"Unknown action type {type}")
	# ENDREGION

	# REGION GIVE HELP
	def giveHelp(self, msgId):
		answer = ""
		courses = ""
		actions = self.mongo.actions.find({})
		for command in actions:
			if command['type'] == "course":
				courses += f"/{command['command']}\n"
				continue

			try:
				answer += f"/{command['command']}: {command['description']}\n"
			except KeyError:
				continue

		answer += "\n<b>I corsi attivi: </b>\n"
		answer += courses
		self.client.send_message(msgId, answer)
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

	

def main():
	"""
	Test
	"""
	app = Client(
		"segretario_log"
	)

	app.run()