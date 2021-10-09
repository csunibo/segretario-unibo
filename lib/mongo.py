from pymongo import MongoClient
import os

def debug(what_to_print):
	print("Using connection string")
	print(what_to_print)

def getClient():
	return MongoClient("localhost", 27017)['segretario']

def getRemoteClient():
	from configparser import ConfigParser
	from urllib.parse import quote_plus
	
	config = ConfigParser()
	config.read("config.ini")
	password = config['mongodb']['PASSWORD']
	encoded_pass = quote_plus(password)
	CONNECTION_STRING = f"mongodb+srv://flecart:{encoded_pass}@segretario.oojgu.mongodb.net/segretario"
	return MongoClient(CONNECTION_STRING)['segretario']

def getContainerClient():
	CONNECTION_STRING = f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{os.environ['MONGODB_HOSTNAME']}:27017"
	debug(CONNECTION_STRING)
	try:
		client = MongoClient(CONNECTION_STRING)['segretario']
	except Exception as e:
		print(f"Ho trovato un errore: {e}")

	return client

# example of importing json with mongoimport, witth drop
# mongoimport --db segretario --collection actions --authenticationDatabase admin --username exampleuser --password nopassword --drop --file actions2.json --jsonArray