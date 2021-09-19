const groups = require('./json/groups.json');
const fs = require('fs');
const { message, formatter, getChatMember } = require('./utils.js');

const getGroup = (chatId, senderId) => {
    if (!(chatId in groups)) {
        groups[chatId] = [];
    }
    const group = groups[chatId];
    if (!group.includes(senderId)) {
        group.push(senderId);
    }

    fs.writeFileSync('json/groups.json', JSON.stringify(groups));
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
    fs.writeFileSync('json/groups.json', JSON.stringify(groups));
    return {status: 200}
}

const getPromises = (group, chatId) => {
    const length = group.length.toString()
    const promises = Array(length);
    group.forEach((userId, i) => {
        promises[i] = getChatMember(chatId, userId.toString());
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

module.exports = {
    replyAfterPromises: replyAfterPromises,
    getPromises: getPromises,
    getGroup: getGroup,
    removeFromGroup: removeFromGroup
}
