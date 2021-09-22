const groups = require('@json/groups.json');
const fs = require('fs');
const { formatter } = require('@lib/utils.js');
const { Bot, message } = require("@lib/bot.js")

// REGION PRIVATE
const getGroup = (chatId, senderId) => {
    if (!(chatId in groups)) {
        groups[chatId] = [];
    }
    const group = groups[chatId];
    if (!group.includes(senderId)) {
        group.push(senderId);
    }

    fs.writeFileSync(groups.filepath, JSON.stringify(groups));
    return group;
}

const removeFromGroup = (msg, notFoundError) => {
    const chatId = msg.chat.id;
    const senderId = msg.from.id;
    const title = msg.chat.title;
    const group = groups[chatId];

    if (!(chatId in groups)) {
        message(msg, formatter(notFoundError, title));
        return {status: 404};
    }

    if (!group.includes(senderId)) {
        message(msg, formatter(notFoundError, title));
        return {status: 404};
    }
    group.splice(group.indexOf(senderId), 1);
    if (group.length == 0) {
        delete groups[chatId];
    }
    fs.writeFileSync(groups.filepath, JSON.stringify(groups));
    return {status: 200}
}

const getPromises = (group, chatId) => {
    const length = group.length.toString()
    const promises = Array(length);
    group.forEach((userId, i) => {
        promises[i] = Bot.getChatMember(chatId, userId.toString());
    });

    return promises;
}

const replyAfterPromises = (msg, promises, group) => {
    const length = group.length.toString()
    var list = formatter(length == '1' ? msg.singularText : msg.pluralText, msg.chat.title, length);

    try {
        Promise.allSettled(promises)
        .then((result) => {
            result.forEach(e => {
                if (e.status === 'fulfilled') {
                    list += e.value;
                }
            });

            message(msg, list);
        });
    } catch(e) {
        console.error(e);
    }
}



function add(msg, action) {
	if (msg.chat.type !== 'group' && msg.chat.type !== 'supergroup') {
		message(msg, action.chatError);
        return
    } 
    const group = getGroup(msg.chat.id, msg.from.id);

    // design-issue: metto sti field in msg perché è più facile da passere in funzione
    // ma non so se è una best-practice, forse c'è un design migliore
    msg.singularText = action.singularText;
    msg.pluralText = action.pluralText;

    const promises = getPromises(group, msg.chat.id);
    replyAfterPromises(msg, promises, group);
}

function remove(msg, action) {
	if (msg.chat.type !== 'group' && msg.chat.type !== 'supergroup') {
		message(msg, action.chatError);
        return;
    }
    const response = removeFromGroup(msg, action.notFoundError);
    if (response.status === 404) {
        return;
    }
    message(msg, formatter(action.text, msg.chat.title));
    return;
}

module.exports = {
    Group: {
		add: add,
		remove: remove
	}
}
