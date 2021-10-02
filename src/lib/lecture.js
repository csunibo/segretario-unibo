const axios = require('axios');
const { message } = require("@lib/bot.js");
const { DateTime, Interval } = require("luxon");

// REGION PRIVATE
const createReplyMessage = (lectures) => {
    let text = '';
        
    for (let i = 0; i < lectures.length; ++i) {
        text += '🕘 <b>' + lectures[i].title + '</b> ' + lectures[i].time + '\n';
    }
	return text;
}

const reply = async (msg, msgText, fallbackText) => {
    if (msgText.length !== 0) {
        const msgId = await message(msg, msgText);
		// console.log(msgId, "replay");
		return msgId;
    } else {
        message(msg, fallbackText);
		return undefined;
    }
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

const _filterDays = (res) => {
	const now = DateTime.now("");
	const startOfWeek = now.startOf("week");
	const endOfNextWeek = startOfWeek.plus({ days: 7 }).endOf("week")

	// to string returns this format '2017-09-14T03:20:34.091-04:00'
	console.log(startOfWeek.toString().substring(0, 10))
	return [startOfWeek.toString().substring(0, 10), endOfNextWeek.toString().substring(0, 10)];
}

// REGION PUBLIC
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

module.exports = {
	lectures: lectures
}