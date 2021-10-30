// Dynamic path requiring https://gist.github.com/branneman/8048520
require('module-alias/register');
const { main } = require("@lib/main.js");

main();


// Using express so heroku doesn't complain about not using web
const express = require('express');
const app = express();
app.use(express.static('public'));

app.get('/', (req, res) => {
	res.send('This is a Telegram bot working.');
})

app.listen(process.env.PORT || 3000, () => {
	console.log(`Example app listening at http://localhost:${process.env.PORT || 3000}`)
})

