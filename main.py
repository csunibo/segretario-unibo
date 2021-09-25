import sys
sys.path.append("lib/")
from bot import Bot

def main():
	Bot().client.run()
	# client = getClient()
	# res = client.actions.count_documents({"command": "help"})
	# print(res)	

if __name__ == "__main__":
	"""
	Qui provavo a far funzionare mongo, funziona, ma la prima connessione è molto lenta
	non funzinoa bene per esssere testata...
	"""
	# client = getClient()
	# client.actions.copyDatabase("segretario", "segretario", "localhost:27018")
	# print(client)
	# res = client.actions.count_documents({"command": "help"})
	# print(res)
	main()