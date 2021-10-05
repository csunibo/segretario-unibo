from pyrogram.types import Message as PyrogramMessage

# TODO: add data section to store data and communicate with other processes
class Message(PyrogramMessage):
	"""
	COSA SERVE QUESTA CLASSE
	È una struttura di dati per rendere più semplice il passaggio id informazioni fra uno script e l'altro
	Tutto quello che il bot manda deve passare da questa classe.
	"""
	def __init__(
		self, 
		pyrogramMessage, 
		text=None, 
		status=None
	) -> None:

		super().__init__(
			message_id=pyrogramMessage.message_id + 1, 
			chat=pyrogramMessage.chat, 
			from_user=pyrogramMessage.from_user, 
			text=text,
			status=status
		)

		self.status = status
