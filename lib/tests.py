import unittest
from freezegun import freeze_time

def getPyrogramMessage():
	""" Create bogus chat for testing """
	from pyrogram.types import Chat 
	from pyrogram.types import User
	from pyrogram.types import Message
	chat = Chat(id=0, type="group", title="bogus")
	from_user = User(id=0)

	return Message(message_id=0, chat=chat, from_user=from_user)

class TestLectures(unittest.TestCase):
	@freeze_time("2012-01-01")
	def test_getUrl(self):
		from lectures import getUrl

		url = "https://example.com?"
		start = 0
		end = 1
		result = getUrl(url, start, end)
		endUrl = "https://example.com?&start=2012-01-01&end=2012-01-02"
		self.assertEqual(endUrl, result)


	@freeze_time("2012-01-31")
	def test_getUrl_nextMonth(self):
		from lectures import getUrl

		url = "https://example.com?"
		start = 0
		end = 1
		result = getUrl(url, start, end)
		endUrl = "https://example.com?&start=2012-01-31&end=2012-02-01"
		self.assertEqual(endUrl, result)


	@freeze_time("2012-12-31")
	def test_getUrl_nextYear(self):
		from lectures import getUrl

		url = "https://example.com?"
		start = 0
		end = 1
		result = getUrl(url, start, end)
		endUrl = "https://example.com?&start=2012-12-31&end=2013-01-01"
		self.assertEqual(endUrl, result)


	@freeze_time("2021-10-06")
	def test_get_lecture_today(self):
		from lectures import get_lectures
		from message import Message

		url = "https://corsi.unibo.it/laurea/informatica/orario-lezioni/@@orario_reale_json?anno=1"
		data = {
			'url': url,
			'isTomorrow': False,
			"fallbackText": "qualcosa" # questa entry è da eliminare, deve stare in db per errori e non action
		}
		msg = Message(getPyrogramMessage(), data=data)

		endMsg = "🕘 <b> LOGICA PER L'INFORMATICA (9 CFU) / (1) Modulo 1 </b>  09:00 - 11:00 \n🕘 <b> PROGRAMMAZIONE / (1) Modulo 1 </b>  11:00 - 14:00 \n"
		testMsg = get_lectures(msg).text
		self.assertEqual(endMsg, testMsg)


	@freeze_time("2021-10-05")
	def test_get_lecture_tomorrow(self):
		from lectures import get_lectures
		from message import Message

		url = "https://corsi.unibo.it/laurea/informatica/orario-lezioni/@@orario_reale_json?anno=1"
		data = {
			'url': url,
			'isTomorrow': True,
			"fallbackText": "qualcosa" # questa entry è da eliminare, deve stare in db per errori e non action
		}
		msg = Message(getPyrogramMessage(), data=data)

		endMsg = "🕘 <b> LOGICA PER L'INFORMATICA (9 CFU) / (1) Modulo 1 </b>  09:00 - 11:00 \n🕘 <b> PROGRAMMAZIONE / (1) Modulo 1 </b>  11:00 - 14:00 \n"
		testMsg = get_lectures(msg).text
		self.assertEqual(endMsg, testMsg)


	def test_getCourses(self):
		from lectures import getCourse
		from message import Message

		data = {
			"professors": ["Tizio.bello", "Altro.tizio"],
			"name": "TomJerry",
			"virtuale": "aaaa",
			"teams": "bbbb",
			"website": "0000"
		}

		endMsg = """<b>TomJerry</b>
		<a href='https://virtuale.unibo.it/course/view.php?id=aaaa'>Virtuale</a>
		<a href='https://teams.microsoft.com/l/meetup-join/19%3ameeting_bbbb%40thread.v2/0?context=%7b%22Tid%22%3a%22e99647dc-1b08-454a-bf8c-699181b389ab%22%2c%22Oid%22%3a%22080683d2-51aa-4842-aa73-291a43203f71%22%7d'>Videolezione</a>
		<a href='https://www.unibo.it/it/didattica/insegnamenti/insegnamento/0000'>Sito</a>
		<a href='https://www.unibo.it/it/didattica/insegnamenti/insegnamento/0000/orariolezioni'>Orario</a>
		Tizio.bello@unibo.it\n  Altro.tizio@unibo.it"""

		msg = Message(getPyrogramMessage(), data=data)
		testMsg = getCourse(msg).text
		self.assertEqual(endMsg, testMsg)


class TestCourses(unittest.TestCase):
	def __init__(self, *args, **kwargs) -> None:
		from lookForGroups import LookForGroups
		super().__init__(*args, **kwargs)
		self.groups = LookForGroups()		


	def test_add_and_remove(self):
		pyroMessage = getPyrogramMessage()
		testMsg = self.groups.add(pyroMessage).text 
		endMsg = f"Questi utenti cercano gruppo in {pyroMessage.chat.title}"
		self.assertEqual(testMsg, endMsg)

		testMsg = self.groups.remove(pyroMessage).text
		endMsg = "Utente rimosso con Successo!"
		self.assertEqual(testMsg, endMsg)


	def test_addTwice_and_removeTwice(self):
		pyroMessage = getPyrogramMessage()

		testMsg = self.groups.add(pyroMessage).text 
		endMsg = f"Questi utenti cercano gruppo in {pyroMessage.chat.title}"
		self.assertEqual(testMsg, endMsg)

		testMsg = self.groups.add(pyroMessage).text 
		endMsg = f"Questi utenti cercano gruppo in {pyroMessage.chat.title}"
		self.assertEqual(testMsg, endMsg)

		testMsg = self.groups.remove(pyroMessage).text
		endMsg = "Utente rimosso con Successo!"
		self.assertEqual(testMsg, endMsg)

		testMsg = self.groups.remove(pyroMessage).text
		endMsg = f"Utente non trovato nella chat <b>{pyroMessage.chat.title}</b>"
		self.assertEqual(testMsg, endMsg)

if __name__ == '__main__':
	unittest.main()