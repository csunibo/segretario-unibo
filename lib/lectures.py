import requests
import calendar
from datetime import date, datetime
import json
from message import Message

def get_lectures(msg: Message, data: object, isTomorrow: bool = False) -> Message:
	"""
	Receives msg dict, gets the lectures and answers back, you have to change
	other params to make it as you like
	"""
	if not data['url'] or not data['fallbackText']:
		return Message(msg, text="Ho problemi a trovare le lezioni, devo essere sistemato!", status=500)

	response = requests.get(data["url"]).text
	response = json.loads(response)
	lectures = _formatLectures(response, isTomorrow)
	res = _reply(msg, lectures, data['fallbackText'])
	return res


def _formatLectures(response, isTomorrow: bool):
	now = datetime.now()

	# variabile usata per cercare lezioni di oggi o domani
	answer = []
	for lezione in response:
		lesson_time = datetime.strptime(lezione['start'], "%Y-%m-%dT%H:%M:%S")
		date_to_check = _getDateCheck(lesson_time, isTomorrow)
		if lesson_time.year == now.year and lesson_time.month == now.month and lesson_time.day == date_to_check:
			answer.append(lezione)

	answer.sort(key= lambda x: x['start'])
	return answer


def _getDateCheck(lesson_time, isTomorrow):
	# ISSUE: is this function too much complicated? can this be made more intuitive somehow?
	now = datetime.now()
	setDate = 1 if isTomorrow else 0
	# BUG: se è l'ultimo giorno dell'anno non funziona isTomowrro, ma spero nessono
	# usi il bot l'ultimo dell'anno lel
	last_day_of_month = calendar.monthrange(now.year, now.month)[1]
	date_to_check = (now.day + setDate) % (last_day_of_month + 1)

	# se è veramente l'ultimo giorno allora il risultato sarà 0
	if date_to_check == 0:
		date_to_check = 1
	return date_to_check


def _reply(msg, lectures, fallbackText) -> Message:
	if len(lectures) == 0:
		return Message(msg, text=fallbackText)

	ans = ''

	for lecture in lectures:
		ans += f"🕘 <b> {lecture['title']} </b>  {lecture['time']} \n"
	return Message(msg, text=ans)


def getCourse(msg, courseInfo) -> Message:
		# Non inviare link malformati, controlla prima il json
		if not courseInfo["professors"] or not courseInfo["virtuale"] or not courseInfo["teams"] or not courseInfo["website"]:
			return Message(msg.chat.id, "Non riesco a ritrovare il corso!", status=404)

		emails = '@unibo.it\n  '.join(courseInfo["professors"]) + '@unibo.it'
		return Message(msg.chat.id, f"""<b>{courseInfo["name"]}</b>
			<a href='https://virtuale.unibo.it/course/view.php?id={courseInfo["virtuale"]}'>Virtuale</a>
			<a href='https://teams.microsoft.com/l/meetup-join/19%3ameeting_{courseInfo["teams"]}%40thread.v2/0?context=%7b%22Tid%22%3a%22e99647dc-1b08-454a-bf8c-699181b389ab%22%2c%22Oid%22%3a%22080683d2-51aa-4842-aa73-291a43203f71%22%7d'>Videolezione</a>
			<a href='https://www.unibo.it/it/didattica/insegnamenti/insegnamento/{courseInfo["website"]}'>Sito</a>
			<a href='https://www.unibo.it/it/didattica/insegnamenti/insegnamento/{courseInfo["website"]}/orariolezioni'>Orario</a>
			{emails}""")