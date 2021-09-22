const fs = require('fs');
const { message: std_message } = require("@lib/utils.js")

// REGION PRIVATE
const getSleep = () => {
    const sleeps = require("@json/sleep.json");
    return sleeps;
}

const getRandomLine = () => {
    const lines = require("@json/lines.json");
    const sleepLines = lines.sleep;
    const randomChoice = Math.floor(Math.random() * sleepLines.length);
    return sleepLines[randomChoice];
}

const message = (sleeps) => {
	const groups = sleeps.groups;
    Object.keys(groups).forEach(groupId => {
		const group = groups[groupId];
		const currTimestamp = new Date().getTime();
        if (group.is_sleep && currTimestamp - group.last_call > group.time_cutoff) {
            const msgObject = {
                chat: {
                    id: groupId
                }
            }
            std_message(msgObject, getRandomLine());
        }
    });
}

const saveCall = (msg, sleeps) => {
    const chatId = msg.chat.id;
    const groups = sleeps.groups;

    // save the group id
    if (!(chatId in groups)) {
        try {
            groups[chatId] = {
                "is_sleep": true,
                "last_call": new Date().getTime(),
                "time_cutoff": sleeps.std_time_cutoff // 6 ore, check 22/09
            }
            sleeps.groups = groups;
            fs.writeFileSync(sleeps.filepath, JSON.stringify(sleeps));
        } catch(e) {
            console.error(e);
            console.log("Problem in adding the group to the known ones");
        }
    } else {
		groups[chatId].last_call = new Date().getTime();
	}

    // TODO: save logs
}

// REGION PUBLIC
const receive = (msg) => {
    // SEE SLEEP.JSON for sleeps structure.
    const sleeps = getSleep();
	// WARNING: don't change the order of std_message and saveCall
    message(sleeps);
    saveCall(msg, sleeps);
}

const toggle = (msg) => {
	try {
		const sleeps = getSleep();
		const currentGroup = sleeps.groups[msg.chat.id];
		currentGroup.is_sleep = currentGroup.is_sleep ? false : true;
		fs.writeFileSync(sleeps.filepath, JSON.stringify(sleeps));
		std_message(msg, `Messaggi sleep di segretario importati su ${currentGroup.is_sleep ? "attivati" : "disattivati"}`);
	} catch(e) {
		console.error(e);
		console.log("Couldn't toggle the sleep feature");
	}
}

module.exports = {
	Sleep: {
		receive: receive,
		toggle: toggle
	}
}