const { Client, IntentsBitField } = require('discord.js');
const { get, put } = require('@vercel/blob');
const client = new Client({ intents: [IntentsBitField.Flags.Guilds, IntentsBitField.Flags.GuildMessages, IntentsBitField.Flags.DirectMessages, IntentsBitField.Flags.MessageContent] });

client.once('ready', () => console.log('Bot ready!'));

client.on('messageCreate', async (message) => {
  if (message.author.bot) return;
  if (message.content === 'Y' || message.content === 'N') {
    const stagId = 1; // Placeholder—map Discord user to Stag ID later
    const { data } = await get(`novenas/${stagId}.json`);
    if (data) {
      const novena = JSON.parse(data);
      const responses = novena.responses || { "1": null, "2": null, "3": null, "4": null, "5": null, "6": null, "7": null, "8": null, "9": null };
      const day = Math.min(Object.keys(responses).filter(d => !responses[d]).map(Number)[0], 9);
      responses[day] = message.content === 'Y';
      novena.responses = responses;
      await put(`novenas/${stagId}.json`, JSON.stringify(novena), { access: 'public' });
    }
  }
});

client.login(process.env.DISCORD_BOT_TOKEN);

async function sendPrompt(stagId, userId, day, time) {
  const prompts = require('../data/prompts.json');
  const user = await client.users.fetch(userId);
  const message = prompts[`Day ${day}`][time];
  user.send(message);
}

module.exports = { sendPrompt };