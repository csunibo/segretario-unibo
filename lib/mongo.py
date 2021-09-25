from pymongo import MongoClient

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