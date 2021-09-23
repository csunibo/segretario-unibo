const TelegramBot = require('node-telegram-bot-api');
const settings = require('@json/settings.json');

const bot = new TelegramBot(process.env.API_KEY, {polling: true});

// TODO: sarebbe bello avere una classe bot che eredity la classe telegrambot.
// Issue: this functions should just get msg.chat.id, not the whole object.
const message = (msg, text) => {
    // TODO: write asserts to check or fail if msg, text or settings are undefined
    // this is valid for everyfuncion
	return bot.sendMessage(msg.chat.id, text, settings.messageOptions)
	.then(res => {
		return res.message_id;
	})
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
        const user = result.user;
        return `👤 <a href='tg://user?id=${user.id}'>${user.first_name}${user.last_name ? ' ' + user.last_name : ''}</a>\n`;
    });
}

const pinChatMessage = (chat_id, message_id) => {
	bot.pinChatMessage(chat_id, message_id)
	.catch(e => {
		console.error(e.stack);
		console.log("Non sono riuscito a pinnare un messaggio");
	})
}
module.exports = {
	Bot: {
		start: start,
		getChatMember: getChatMember,
		pinChatMessage: pinChatMessage,
		settings: settings
	},
	message: message
}