import json
from mongo import getClient

# TODO: create custom class for the responses
# these responses are repeating themselves too much
class LookForGroups():
	def __init__(self):
		self.mongo = getClient()

	def saveToGroup(self, chatId, senderId):
		is_group = self.mongo.lookgroups.count_documents({"chatId": chatId})
		if is_group == 0:
			self.mongo.lookgroups.insert({
				"chatId": chatId,
				"senderIds": [senderId]
			})

		in_group = self.mongo.lookgroups.count_documents({
			"chatId": chatId,
			"senderIds": senderId
		})
		if in_group == 0:
			self.mongo.lookgroups.update(
				{"chatId": chatId},
				{"$push": {
					"senderIds": senderId
				}})
		# BUG:This code is checking for documents, not checking for array occurences
		# change as described https://stackoverflow.com/questions/14319616/how-to-count-occurence-of-each-value-in-array
		elif in_group > 1:
			raise Exception(f"Same person with ID {senderId} added multiple times in group {chatId}")

		return {
			"status": 200,
			"remove": False,
			"chatId": chatId
		}

	def removeFromGroup(self, chatId, senderId):

		in_group = self.mongo.lookgroups.count_documents({
			"chatId": chatId,
			"senderIds": senderId
		})
		if in_group == 0:
			return {
				"status": 404,
				"chatId": chatId
			}
		elif in_group > 1:
			raise Exception(f"Found duplicate chat with chatId {chatId}")

		self.mongo.lookgroups.update(
			{"chatId": chatId},
			{"$pull": {
				"senderIds": senderId
			}})
		
		return {
			"status": 200,
			"remove": True,
			"chatId": chatId
		}

	def add(self, msg):
		if msg.chat.type != "group" and msg.chat.type != "supergroup":
			return {
				"status": 403,
				"chatId": msg.chat.id
			}
		
		return self.saveToGroup(msg.chat.id, msg.from_user.id)

	def remove(self, msg):
		if msg.chat.type != "group" and msg.chat.type != "supergroup":
			return {
				"status": 403,
				"chatId": msg.chat.id
			}

		return self.removeFromGroup(msg.chat.id, msg.from_user.id)