# A pensarci un pò potremmo copiare la classe message di pyrogram ed espanderlo........
# ma non ci ho pensato quando ho creato questa :D
# TODO: refactorare con la classe di Pyrogram
class Message():
	"""
	COSA SERVE QUESTA CLASSE
	È una struttura di dati per rendere più semplice il passaggio id informazioni fra uno script e l'altro
	Tutto quello che il bot manda deve passare da questa classe.

	Per ora, 04/10/21 Supporta solo text
	"""
	# TODO: this init is not nice too look at, is there a way to make it nicer?
	def __init__(self, chatId, text, title="No title", senderIds=None, status=200, chatType=None, *args, **kwargs) -> None:
		self.chatId = chatId
		self.text = text
		self.senderIds=senderIds
		self.status = status
		self.title = title
		self.chatType = chatType

		# TODO: capire se args e kwargs servono a qualcosa
		self.otherArgs=args
		self.otherKwargs=kwargs

	def __str__(self) -> str:
		return f"Messaggio diretto a {self.chatId}, con testo {self.text}"