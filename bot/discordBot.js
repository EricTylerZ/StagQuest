const { Client, IntentsBitField } = require('discord.js');
const client = new Client({ intents: [IntentsBitField.Flags.Guilds, IntentsBitField.Flags.GuildMessages, IntentsBitField.Flags.DirectMessages, IntentsBitField.Flags.MessageContent] });

client.once('ready', () => console.log('Bot ready!'));

client.on('messageCreate', async (message) => {
  if (message.author.bot) return;
  if (message.content === 'Y' || message.content === 'N') {
    // Placeholder: Link to Stag ID via DB (needs user mapping)
    const stagId = 1; // Hardcoded for now
    const { Pool } = require('pg');
    const pool = new Pool({ connectionString: process.env.POSTGRES_URL });
    const { rows } = await pool.query('SELECT responses FROM novenas WHERE stag_id = $1', [stagId]);
    if (rows[0]) {
      const responses = rows[0].responses;
      const day = Math.min(Object.keys(responses).filter(d => !responses[d]).map(Number)[0], 9);
      responses[day] = message.content === 'Y';
      await pool.query('UPDATE novenas SET responses = $1 WHERE stag_id = $2', [JSON.stringify(responses), stagId]);
    }
  }
});

client.login(process.env.DISCORD_BOT_TOKEN);

async function sendPrompt(stagId, userId, day, time) {
  const prompts = require('./prompts.json');
  const user = await client.users.fetch(userId);
  const message = prompts[`Day ${day}`][time];
  user.send(message);
}

module.exports = { sendPrompt };