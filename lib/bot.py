from pyrogram import Client
from pyrogram.handlers import MessageHandler
import json

from lectures import getCourse, get_lectures
from mongo import getClient

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
			Group.add(msg)
		elif type == 'notLookingFor':
			Group.remove(msg)
		elif type == "toggleSleep":
			Sleep.toggle(msg)
		else:
			raise TypeError(f"Unknown action type {type}")

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
	

def main():
	"""
	Test
	"""
	app = Client(
		"segretario_log"
	)

	app.run()