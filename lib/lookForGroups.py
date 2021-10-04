from pyrogram.types import messages_and_media
from mongo import getClient
from message import Message

# TODO: create custom class for the responses
# these responses are repeating themselves too much
class LookForGroups():
	def __init__(self):
		self.mongo = getClient()

	def saveToGroup(self, message: Message):

		is_group = self.mongo.lookgroups.count_documents({"chatId": message.chatId})
		if is_group == 0:
			self.mongo.lookgroups.insert({
				"chatId": message.chatId,
				"senderIds": [message.senderIds]
			})

		in_group = self.mongo.lookgroups.count_documents({
			"chatId": message.chatId,
			"senderIds": message.senderIds
		})
		if in_group == 0:
			self.mongo.lookgroups.update(
				{"chatId": message.chatId},
				{"$push": {
					"senderIds": message.senderIds
				}})

		# TODO: should not validate from here but should add validators in the database!
		# BUG:This code is checking for documents, not checking for array occurences
		# change as described https://stackoverflow.com/questions/14319616/how-to-count-occurence-of-each-value-in-array
		elif in_group > 1:
			raise Exception(f"Same person with ID {message.senderIds} added multiple times in group {message.chatId}")
		
		message.text = "Questi utenti cercano gruppo in {0}"
		message.text = message.text.format(message.title)
		return message

	def removeFromGroup(self, message: Message):
		in_group = self.mongo.lookgroups.count_documents({
			"chatId": message.chatId,
			"senderIds": message.senderIds
		})
		
		if in_group == 0:
			message.status = 404
			message.text = "Utente non trovato nella chat {0}"
			message.text = message.text.format(message.title)
			return message 
		elif in_group > 1:
			raise Exception(f"Found duplicate chat with chatId {message.chatId}")

		self.mongo.lookgroups.update(
			{"chatId": message.chatId},
			{"$pull": {
				"senderIds": message.senderIds
			}})
		
		message.text = "Utente rimosso con Successo!"
		return message

	def add(self, msg: Message):
		if msg.chatType != "group" and msg.chatType != "supergroup":
			msg.status = 403
			msg.text = "Questa funzionalità deve essere usata nei gruppi non nelle chat private!"
			return msg
		
		return self.saveToGroup(msg)

	def remove(self, msg: Message):
		if msg.chatType != "group" and msg.chatType != "supergroup":
			msg.status = 403
			msg.text = "Questa funzionalità deve essere usata nei gruppi non nelle chat private!"
			return msg

		return self.removeFromGroup(msg)