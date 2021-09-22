const TelegramBot = require('node-telegram-bot-api');
const settings = require('@json/settings.json');

const bot = new TelegramBot(process.env.API_KEY, {polling: true});

const message = (msg, text) => {
    // TODO: write asserts to check or fail if msg, text or settings are undefined
    // this is valid for everyfuncion
	bot.sendMessage(msg.chat.id, text, settings.messageOptions)
	.catch(e => console.error(e));
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
	Bot: {
		start: start,
		getChatMember: getChatMember,
		settings: settings
	},
	message: message
}