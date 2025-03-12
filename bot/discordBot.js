const { Client, GatewayIntentBits } = require('discord.js');
const { get, put } = require('@vercel/blob');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.DirectMessages,
  ],
});

client.on('ready', () => {
  console.log('Bot is ready!');
  // Check novenas every minute
  setInterval(checkNovenas, 60000);
});

async function checkNovenas() {
  const { blobs } = await get({ prefix: 'novenas/' });
  for (const blob of blobs) {
    const novena = JSON.parse(blob.data);
    const startTime = new Date(novena.start_time);
    const now = new Date();
    const utcOffset = parseInt(novena.timezone); // e.g., -7
    const localTime = new Date(now.getTime() + utcOffset * 60 * 60 * 1000);
    const daysElapsed = Math.floor((localTime - startTime) / (1000 * 60 * 60 * 24));

    if (daysElapsed < 9 && novena.current_day <= daysElapsed + 1) {
      try {
        const user = await client.users.fetch(novena.discord_id);
        await user.send(`Day ${novena.current_day} of your novena for Stag ID ${novena.stag_id}. Keep it up!`);
        novena.current_day++;
        await put(`novenas/${novena.stag_id}.json`, JSON.stringify(novena), { access: 'public' });
      } catch (error) {
        console.error(`Failed to send DM for stag ${novena.stag_id}:`, error);
      }
    }
  }
}

client.on('messageCreate', async (message) => {
  if (message.author.bot) return;
  console.log('Received message from', message.author.id, ':', message.content);

  try {
    if (message.content.startsWith('!')) {
      // Handle commands (e.g., !help)
    } else {
      // Handle novena responses
      const userId = message.author.id;
      message.reply('Your response has been recorded.');
    }
  } catch (error) {
    console.error('Error handling message:', error);
    message.reply('An error occurred while processing your response.');
  }
});

client.login(process.env.DISCORD_BOT_TOKEN);