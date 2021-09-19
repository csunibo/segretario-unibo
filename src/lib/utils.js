const TelegramBot = require('node-telegram-bot-api');
const settings = require('@json/settings.json');

const bot = new TelegramBot(process.env.API_KEY, {polling: true});
console.log(process.env.API_KEY)

// BUG: non funziona non so perché
const assert = (value, test, boolean=true) => {
    if ( (boolean && value !== test) || (!boolean && value === test) ) {
        console.log(`assert with ${value} and ${test} failed`)
        throw TypeError();
    }

    return;
}

const message = (msg, text) => {
    // TODO: write asserts to check or fail if msg, text or settings are undefined
    // this is valid for everyfuncion
	bot.sendMessage(msg.chat.id, text, settings.messageOptions)
	.catch(e => console.error(e));
}

const getTodayLectures = (res) => {
    let now = new Date();
    let todayLectures = [];
    for (let i = 0; i < res.data.length; ++i) {
        let start = new Date(res.data[i].start);
        if (start.getFullYear() === now.getFullYear() && start.getMonth() === now.getMonth() && start.getDate() === now.getDate()) {
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

// String formatting via placeholders: has troubles with placeholders injections
// e.g. flecart: ho fatto una prova e sembra trasformare "test" in <b>"test"</b>
// Ma non so la logica con cui lo faccia....
// Non ho capito come funziona, ma funziona. :))))))
const formatter = function () {
    var s = arguments[0].slice();
    for (var i = 0; i < arguments.length - 1; ++i) {
        s = s.replace(new RegExp("\\{" + i + "\\}", "gm"), arguments[i + 1]);
    }
    return s;
}

const replyWithTodaylecture = (msg, todayLectures, fallbackText) => {
    let text = '';
        
    for (let i = 0; i < todayLectures.length; ++i) {
        text += '🕘 <b>' + todayLectures[i].title + '</b> ' + todayLectures[i].time + '\n';
    }
    if (todayLectures.length !== 0) {
        message(msg, text);
    } else {
        message(msg, fallbackText);
    }
}

const start = (startingFunction) => {
    bot.on('message', startingFunction);
}

const getChatMember = (chatId, userId) => {
    // What if this function fails to get the user? Should make a catch
    // but i don't know what to return then, or i don't know what
    // bot.getChatMember returns...
    return bot.getChatMember(chatId, userId.toString())
    .then((result) => {
        console.log(result)
        const user = result.user;
        return `👤 <a href='tg://user?id=${user.id}'>${user.first_name}${user.last_name ? ' ' + user.last_name : ''}</a>\n`;
    });
}

module.exports = {
    formatter: formatter,
    getTodayLectures: getTodayLectures,
    replyWithTodaylecture: replyWithTodaylecture,
    message: message,
    settings: settings,
    start: start,
    getChatMember: getChatMember

}
