import requests
import calendar
from datetime import time, timedelta, datetime
import json
from message import Message

def get_lectures(msg: Message) -> Message:
	"""
	Receives msg dict, gets the lectures and answers back, you have to change
	other params to make it as you like
	"""
	data = msg.data
	if not data['url'] or not data['fallbackText']:
		return Message(msg, text="Ho problemi a trovare le lezioni, devo essere sistemato!", status=500)

	if data['isTomorrow']:
		url = getUrl(data['url'], start=1, end=1)
	else:
		url = getUrl(data['url'], start=0, end=0)

	response = requests.get(url).text
	lectures = json.loads(response)
	res = _reply(msg, lectures, data['fallbackText'])
	return res

def getUrl(url, start=0, end=0):
	"""
	Gets Unibo url and returns the url with range from the day start (offset from today)
	and the day end, offset from today.
	Es: TODAY is 06/10/2021, start=1, end = 3 gets this range:
	07/10 - 09/10
	"""
	today = datetime.now()
	startDay = today + timedelta(days=start)
	endDay = today + timedelta(days=end)

	# Returns similiar to url+&start=2021-12-10&end=2021-12-11
	return f"{url}&start={startDay.strftime('%Y-%m-%d')}&end={endDay.strftime('%Y-%m-%d')}"

def _getDateCheck(isTomorrow):
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


def getCourse(msg: Message) -> Message:
	courseInfo = msg.data
	# Non inviare link malformati, controlla prima il json
	if not courseInfo["professors"] or not courseInfo["virtuale"] or not courseInfo["teams"] or not courseInfo["website"]:
		return Message(msg, text="Non riesco a ritrovare il corso!", status=404)

	emails = '@unibo.it\n  '.join(courseInfo["professors"]) + '@unibo.it'
	return Message(msg, text=f"""<b>{courseInfo["name"]}</b>
		<a href='https://virtuale.unibo.it/course/view.php?id={courseInfo["virtuale"]}'>Virtuale</a>
		<a href='https://teams.microsoft.com/l/meetup-join/19%3ameeting_{courseInfo["teams"]}%40thread.v2/0?context=%7b%22Tid%22%3a%22e99647dc-1b08-454a-bf8c-699181b389ab%22%2c%22Oid%22%3a%22080683d2-51aa-4842-aa73-291a43203f71%22%7d'>Videolezione</a>
		<a href='https://www.unibo.it/it/didattica/insegnamenti/insegnamento/{courseInfo["website"]}'>Sito</a>
		<a href='https://www.unibo.it/it/didattica/insegnamenti/insegnamento/{courseInfo["website"]}/orariolezioni'>Orario</a>
		{emails}""")