from mongo import getContainerClient
from message import Message

class LookForGroups():
	def __init__(self):
		self.mongo = getContainerClient()

	def saveToGroup(self, message: Message):
		is_group = self.mongo.lookgroups.count_documents({"chatId": message.chat.id})
		if is_group == 0:
			res = self.mongo.lookgroups.insert_one({
				"chatId": message.chat.id,
				"senderIds": [message.from_user.id]
			})
			print(res)

		in_group = self.mongo.lookgroups.count_documents({
			"chatId": message.chat.id,
			"senderIds": message.from_user.id
		})
		if in_group == 0:
			self.mongo.lookgroups.update_one(
				{"chatId": message.chat.id},
				{"$push": {
					"senderIds": message.from_user.id
				}})

		# TODO: should not validate from here but should add validators in the database!
		# BUG:This code is checking for documents, not checking for array occurences
		# change as described https://stackoverflow.com/questions/14319616/how-to-count-occurence-of-each-value-in-array
		elif in_group > 1:
			raise Exception(f"Same person with ID {message.from_user.id} added multiple times in group {message.chat.id}")
		
		message.text = "Questi utenti cercano gruppo in {0}"
		message.text = message.text.format(message.chat.title)
		return message

	def removeFromGroup(self, message: Message):
		in_group = self.mongo.lookgroups.count_documents({
			"chatId": message.chat.id,
			"senderIds": message.from_user.id
		})
		
		if in_group == 0:
			message.status = 404
			message.text = "Utente non trovato nella chat <b>{0}</b>"
			message.text = message.text.format(message.chat.title)
			return message 
		elif in_group > 1:
			raise Exception(f"Found duplicate chat with chatId {message.chat.id}")

		self.mongo.lookgroups.update_one(
			{"chatId": message.chat.id},
			{"$pull": {
				"senderIds": message.from_user.id
			}})
		
		message.text = "Utente rimosso con Successo!"
		return message

	def add(self, msg: Message):
		if msg.chat.type != "group" and msg.chat.type != "supergroup":
			msg.status = 403
			msg.text = "Questa funzionalità deve essere usata nei gruppi non nelle chat private!"
			return msg

		return self.saveToGroup(msg)

	def remove(self, msg: Message):
		if msg.chat.type != "group" and msg.chat.type != "supergroup":
			msg.status = 403
			msg.text = "Questa funzionalità deve essere usata nei gruppi non nelle chat private!"
			return msg

		return self.removeFromGroup(msg)