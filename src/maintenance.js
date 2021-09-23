require('module-alias/register');
const { Bot, message } = require("@lib/bot.js");

const onMessage = (msg) => {
	if (!msg.text || msg.text.toString()[0] != '/') {
		return;
	}
	message(msg, "Sono sotto manutenzione! 5 minuti e dovrei essere di nuovo on!");
}

const main = () => {
	if (process.argv.length != 2) {
		console.log('usage: [API_KEY env-var] node index.js');
	}
	process.env.NTBA_FIX_319 = 1;

	Bot.start(onMessage);
}
main();