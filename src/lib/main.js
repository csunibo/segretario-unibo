const actions = require('@json/actions.json');
const memes = require('@json/memes.json');

const { lectures, weekLectures } = require("@lib/lecture.js");
const { Bot, message} = require("@lib/bot.js");


// Autogenerated courses info
function course(msg, courseObject) {
    // TODO, assert that the object is well formed, check that virtuale, teams, website are strings
    // and professors is a list
	const emails = courseObject.professors.join('@unibo.it\n  ') + '@unibo.it';
	message(msg, `<b>${courseObject.name}</b>
	<a href='https://virtuale.unibo.it/course/view.php?id=${courseObject.virtuale}'>Virtuale</a>
	<a href='https://teams.microsoft.com/l/meetup-join/19%3ameeting_${courseObject.teams}%40thread.v2/0?context=%7b%22Tid%22%3a%22e99647dc-1b08-454a-bf8c-699181b389ab%22%2c%22Oid%22%3a%22080683d2-51aa-4842-aa73-291a43203f71%22%7d'>Videolezione</a>
	<a href='https://www.unibo.it/it/didattica/insegnamenti/insegnamento/${courseObject.website}'>Sito</a>
	<a href='https://www.unibo.it/it/didattica/insegnamenti/insegnamento/${courseObject.website}/orariolezioni'>Orario</a>
	${emails}`);
}


const giveHelp = (msg) => {
	answer = "";
	courses = "";
	for (command in actions) {
		if (actions[command].description === undefined) {
            continue;
        }
        if (actions[command].type === "course") {
            courses += `/${command}\n`
			continue;
        }

        try {
            answer += `/${command}: ${actions[command].description}\n`
        } catch(e) {
            console.error(e);
            console.log("Malformed action JSON");
        }
	}

    // rendering speciale per i corsi
    answer += "\n<b>I corsi attivi: </b>\n";
    answer += courses;
	message(msg, answer);
}

// Available actions
const act = (msg, action) => {
	switch (action.type) {
		case 'course':
			course(msg, action);
			break;
		case 'message':
			message(msg, action.text);
			break;
		case 'todayLesson':
			lectures(msg, action.url, action.fallbackText, isTomorrow=false);
			break;
		case 'tomorrowLesson':
			lectures(msg, action.url, action.fallbackText, isTomorrow=true);
			break;
		case 'thisWeek':
			weekLectures(msg, action.url, isNext=false);
			break;
		case 'nextWeek':
			weekLectures(msg, action.url, isNext=true);
			break;
		case 'help':
			giveHelp(msg);
			break;
		default:
			console.error(`Unknown action type "${action.type}"`);
	}
}

const onMessage = (msg) => {
	if (!msg.text || msg.text.toString()[0] != '/') {
		return;
	}

	const text = msg.text.toString()
	// '/command@bot param0 ... paramN' -> 'command'
	command = text.toLowerCase().split(' ')[0].substring(1);
	if (command.includes('@')) {
		command = command.substring(0, command.indexOf('@'));
	}
	if (command in actions) {
		act(msg, actions[command]);
	} else if (command in memes) {
		message(msg, memes[command]);
	}
}


function main() {
	if (process.argv.length != 2) {
		console.log('usage: [API_KEY env-var] node index.js');
	}
	process.env.NTBA_FIX_319 = 1;

	Bot.start(onMessage);
}

module.exports = {
	main: main
}
