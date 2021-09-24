from pyrogram import Client
from pyrogram.handlers import MessageHandler

class Bot():
	def __init__(self):
		"""
		Constructor: gets by default config.ini files on project root
		"""
		from json import load
		self.client = Client(
			"segretario_log"
		)
		self.client.add_handler(MessageHandler(self.__onMessage))

		# TODO: the actions and types should be on the database
		# this load is temporary
		# ISSUE: if want to keep paths, we should make a index file
		# to keep all the paths, so we can stay organized
		with open("./src/json/actions.json", encoding="utf8") as actions:
			self.actions = load(actions)
		
	def __onMessage(self, client, msg):
		text = str(msg['text'])
		if not text or text[0] != "/":
			return

		command = text.split(" ")[0]  
		command = text.split("@")[0][1::]
		if command in self.actions:
			self.__act(msg, self.actions[command])

	# ISSUE: le informazioni per far andare le funzioni possiamo passarle così come per oggetti
	# come ha fatto informabot, o passiamo un codice identificativo e poi la funzione cerca le info da solo
	# mandando una query a mongo?
	# Oppure hai altre idee?
	def __act(self, msg, action):
		type = action['type']
		if type == 'course':
			course()
		elif type == 'lookingFor':
			Group.add(msg)
		elif type == 'message':
			self.client.send_message(msg.chat.id)
		elif type == 'notLookingFor':
			Group.remove(msg)
		elif type == 'todayLesson':
			lectures(msg, isTomorrow=False)
		elif type == 'tomorrowLesson':
			lectures(msg, isTomorrow=True)
		elif type == 'help':
			giveHelp(msg)
		elif type == "toggleSleep":
			Sleep.toggle(msg)
		else:
			raise TypeError(f"Unknown action type {type}")
	
def main():
	"""
	Test
	"""
	app = Client(
		"segretario_log"
	)

	app.run()