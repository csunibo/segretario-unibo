// Register needed to understand @ aliases
require('module-alias/register');
const { Bot, message } = require("@lib/bot.js");
const { lectures } = require("@lib/lecture.js");

const main = () => {
	const lezioniDiOggi = require("@json/actions.json")['lezionidioggi'];
	const chatIds = require("@json/daily.json");

	Object.keys(chatIds).forEach(id => {
		const msgObject = {
			chat: {
				id: id
			}
		}
		message(msgObject, "Ciao! Sono il segretario!\n Pensavo che ti potesse far piacere avere i messaggi di oggi!\n Ecco il programma di oggi:");
		lectures(msgObject, lezioniDiOggi.url, lezioniDiOggi.fallbackText, isTomorrow=false)
		.then(message_id => {
			if (message_id !== undefined) {
				Bot.pinChatMessage(id, message_id);
			}
		})
	});
}

main();