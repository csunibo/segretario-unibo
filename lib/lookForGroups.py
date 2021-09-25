import json
from mongo import getClient

# INCOMPLETO, BISOGNA USARE MONGO ANCHE
class LookForGroups():
	def __init__(self):
		self.mongo = getClient()

	def getGroup(self, chatId, senderId):
		if chatId not in self.groups:
			self.groups[chatId] = []

		if senderId not in self.groups[chatId]:
			self.groups[chatId].append(senderId)

		with open("./json/groups.json", "w") as groups:
			groups.write(json.dumps(self.groups))

	def removeFromGroup(self, msg, notFoundError):
		chatId = msg.chat.id
		# senderId = msg.from.id
		title = msg.chat.title
		group = self.groups[chatId]