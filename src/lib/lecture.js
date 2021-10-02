const axios = require('axios');
const { message } = require("@lib/bot.js");
const { DateTime, Interval } = require("luxon");

// README: tutto questo script fa un grandissimo lavoro per filtrare i risultati della call
// agli API dell'università, sarebbe molto più facile direttamente ricevere il risultato voluto
// invece che stare a filtrare, fallo visitatore!


// REGION PUBLIC

// TODO fai diventare questa funzione un decoratore che wrappa nella risposta di axios
function lectures(msg, url, fallbackText, isTomorrow) {
	// Filters the results so that the search space is smaller
	// Gets the start of the week to the end of the next week
	const interval = _filterDays();
	url += `&start=${interval[0]}&end=${interval[1]}`;

	return axios.get(url)
	.then(res => {
		const replyMessage = getLectures(res.data, isTomorrow=isTomorrow);
		const msgId = reply(msg, replyMessage, fallbackText)
		return msgId;
	})
	.catch(e => console.error(e.stack));
}

// TODO è praticamente uguale a lectures, da refactorare con decorators
function weekLectures(msg, url, isNext) {
	const interval = _filterDays();
	url += `&start=${interval[0]}&end=${interval[1]}`;

	return axios.get(url)
	.then(res => {
		const replyMessage = getWeekLectures(res.data, isNext=isNext);
		const msgId = reply(msg, replyMessage, fallbackText="Niente lezioni in settimana")
		return msgId;
	})
	.catch(e => console.error(e.stack));
}

// REGION PRIVATE

const _filterDays = (res) => {
	const now = DateTime.now("");
	const startOfWeek = now.startOf("week");
	const endOfNextWeek = startOfWeek.plus({ days: 7 }).endOf("week")

	// to string returns this format '2017-09-14T03:20:34.091-04:00'
	return [startOfWeek.toString().substring(0, 10), endOfNextWeek.toString().substring(0, 10)];
}

const getLectures = (data, isTomorrow) => {
    let lectures = [];
	data.forEach(lecture => {
		if (_isWantedDay(lecture.start, isTomorrow)) {
            lectures.push(lecture);
        }
	})
    lectures.sort((a, b) => {
        if (a.start > b.start) {
            return 1;
        }
        if (a.start < b.start) {
            return -1;
        }
        return 0;
    });
	const replyMessage = createReplyMessage(lectures);
    return replyMessage;
}

const getWeekLectures = (data, isNext) => {
	// Getting the inteval to check with n ext 8 lines, should make this a func?
	const now = DateTime.now("");
	let startOfWeek = now.startOf("week");
	let endOfWeek = startOfWeek.endOf("week");
	if (isNext) {
		startOfWeek = now.plus({ days: 7 }).startOf("week");
		endOfWeek = startOfWeek.endOf("week");
	}
	const interval = Interval.fromDateTimes(startOfWeek, endOfWeek);

    let lectures = [];
	data.forEach(lecture => {
		if (interval.contains(DateTime.fromISO(lecture.start))) {
            lectures.push(lecture);
        }
	})
    lectures.sort((a, b) => {
        if (a.start > b.start) {
            return 1;
        }
        if (a.start < b.start) {
            return -1;
        }
        return 0;
    });
	const replyMessage = createWeekReplyMessage(lectures, startOfWeek);
    return replyMessage;
}

const _getDateCheck = (now, isTomorrow) => {
    // SetDate variable is used to get the lessons of tomorrow or today
	let setDate = isTomorrow ? 1 : 0
	let lastDayOfMonth = now.daysInMonth;
	let dateToCheck = (now.day + setDate) % (lastDayOfMonth + 1)

	// se è veramente l'ultimo giorno ed è settato flag tomorro allora il risultato sarà 0
	if (dateToCheck === 0) {
		dateToCheck = 1
	}
	return dateToCheck
}

const _getMonthCheck = (now, isTomorrow, dateToCheck) => {
	if (isTomorrow && dateToCheck === 1) {
		return now.month + 1
	}
	return now.month;
}

const _isWantedDay = (lessonTime, isTomorrow) => {
	const now = DateTime.now("");
	const start = DateTime.fromISO(lessonTime);
	// ISSUE: inefficiente perché runnato ogni volta, basterebbe una.
	let dateToCheck = _getDateCheck(now, isTomorrow);
	let monthToCheck = _getMonthCheck(now, isTomorrow, dateToCheck);
	return start.year === now.year && start.month === monthToCheck && start.day === dateToCheck
}

const createWeekReplyMessage = (lectures, startOfWeek) => {
	let text = "";

	// 5 giorni sett iniziando da lunedì, hardcoded 5
	for(let i = 0; i < 5; i++) {
		let dayLecture = dailyLectures(startOfWeek, lectures);
		
		const meseGiornoLezione = startOfWeek.toLocaleString();
		text += `📅<b> Lezioni del ${meseGiornoLezione} </b> \n`
		text += createReplyMessage(dayLecture);
		text += '\n';

		startOfWeek = startOfWeek.plus({days: 1});
	}
	return text
}

const dailyLectures = (dayToCheck, lectures) => {
	let dayLectures = []
	lectures.forEach(lecture => {
		if (DateTime.fromISO(lecture.start).day === dayToCheck.day) {
			dayLectures.push(lecture)
		}
	})
	return dayLectures
}

const createReplyMessage = (lectures) => {
    let text = '';
    for (let i = 0; i < lectures.length; ++i) {
        text += '🕘 <b>' + lectures[i].title + '</b> ' + lectures[i].time + '\n';
    }
	if (lectures.length === 0) {
		text += "Non ci sono lezioni per questo giorno \n"
	}
	return text;
}

const reply = async (msg, msgText, fallbackText) => {
	const msgId = await message(msg, msgText);
	return msgId;
}

module.exports = {
	lectures: lectures,
	weekLectures: weekLectures
}