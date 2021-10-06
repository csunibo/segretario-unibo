import sys
sys.path.append("lib/")
from bot import Bot

def main():
	bot = Bot()
	bot.client.run()

if __name__ == "__main__":
	"""
	Qui provavo a far funzionare mongo, funziona, ma la prima connessione è molto lenta
	non funzinoa bene per esssere testata...
	"""
	main()