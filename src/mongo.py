# Non funziona ancora, lo devo settare
def getClient():
	import os
	from pymongo import MongoClient

	CONNECTION_STRING = f"mongodb+srv://flecart:{os.environ["PASSWORD"]}@segretario.mongodb.net/segretario"