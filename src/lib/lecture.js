const axios = require('axios');
const { message } = require("@lib/bot.js")

// REGION PRIVATE
const reply = (msg, lectures, fallbackText) => {
    let text = '';
        
    for (let i = 0; i < lectures.length; ++i) {
        text += '🕘 <b>' + lectures[i].title + '</b> ' + lectures[i].time + '\n';
    }
    if (lectures.length !== 0) {
        message(msg, text);
    } else {
        message(msg, fallbackText);
    }
}

const getLectures = (res, isTomorrow) => {
    let now = new Date();
    let todayLectures = [];
    // SetDate variable is used to get the lessons of tomorrow or today
    const setDate = isTomorrow ? 1 : 0;
    for (let i = 0; i < res.data.length; ++i) {
        let start = new Date(res.data[i].start);
	    // TODO: fix date for the first of the year
        if (start.getFullYear() === now.getFullYear() && start.getMonth() === now.getMonth() && start.getDate() - setDate === now.getDate()) {
            todayLectures.push(res.data[i]);
        }
    }
    todayLectures.sort((a, b) => {
        if (a.start > b.start) {
            return 1;
        }
        if (a.start < b.start) {
            return -1;
        }
        return 0;
    });
    return todayLectures;
}

// REGION PUBLIC
function lectures(msg, url, fallbackText, isTomorrow) {
	axios.get(url)
	.then(res => {
		const lectures = getLectures(res, isTomorrow=isTomorrow);
		reply(msg, lectures, fallbackText);
	})
	.catch(e => console.error(e.stack));
}

module.exports = {
	lectures: lectures
}