const { Client, GatewayIntentBits } = require('discord.js');
const { get, put } = require('@vercel/blob');

// Initialize Discord client with required intents
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.DirectMessages,
  ],
});

// Bot ready event
client.once('ready', () => {
  console.log(`Bot is online as ${client.user.tag}!`);
  // Start checking novenas every minute
  setInterval(checkNovenas, 60000);
  console.log('Started novena check interval (every 60 seconds).');
});

// Function to check and process novenas
async function checkNovenas() {
  try {
    const { blobs } = await get({ prefix: 'novenas/' });
    if (!blobs || blobs.length === 0) {
      console.log('No novenas found in Blob storage.');
      return;
    }

    const times = { 'Matins': 2.5, 'Lauds': 6, 'Terce': 9, 'Sext': 12, 'None': 15, 'Vespers': 18, 'Compline': 21 };

    for (const blob of blobs) {
      const novena = JSON.parse(blob.data);
      const startTime = new Date(novena.start_time);
      const now = new Date();
      const utcOffset = parseInt(novena.timezone); // e.g., -7
      const localTime = new Date(now.getTime() + utcOffset * 60 * 60 * 1000);
      const daysElapsed = Math.floor((localTime - startTime) / (1000 * 60 * 60 * 24));
      const hour = localTime.getHours() + localTime.getMinutes() / 60;
      const currentTime = Object.keys(times).find(t => Math.abs(hour - times[t]) < 1) || null;

      if (daysElapsed < 9 && novena.current_day <= daysElapsed + 1 && currentTime) {
        try {
          const user = await client.users.fetch(novena.discord_id);
          const prayerName = currentTime || 'Daily Update';
          await user.send(`Day ${novena.current_day} of your novena for Stag ID ${novena.stag_id}. Prayer: ${prayerName}. Keep it up!`);
          
          // Only increment day at Compline (end of day)
          if (currentTime === 'Compline') {
            novena.current_day = Math.min(daysElapsed + 1, 9);
            await put(`novenas/${novena.stag_id}.json`, JSON.stringify(novena), { access: 'public' });
            console.log(`Updated novena ${novena.stag_id} to day ${novena.current_day}`);
          }
        } catch (error) {
          console.error(`Failed to process novena for stag ${novena.stag_id}:`, error);
        }
      }
    }
  } catch (error) {
    console.error('Error in checkNovenas:', error);
  }
}

// Handle incoming messages
client.on('messageCreate', async (message) => {
  if (message.author.bot) return;

  console.log(`Received message from ${message.author.id}: ${message.content}`);

  try {
    if (message.content.startsWith('!')) {
      const args = message.content.slice(1).split(' ');
      const command = args.shift().toLowerCase();

      if (command === 'ping') {
        await message.reply('Pong!');
      } else if (command === 'help') {
        await message.reply('Commands: !ping, !help');
      }
    } else {
      // Optionally handle novena responses here
      await message.reply('Your response has been recorded.');
    }
  } catch (error) {
    console.error('Error handling message:', error);
    await message.reply('An error occurred while processing your request.');
  }
});

// Handle bot errors and disconnections
client.on('error', (error) => {
  console.error('Bot encountered an error:', error);
});

client.on('shardDisconnect', (event, id) => {
  console.log(`Shard ${id} disconnected. Code: ${event.code}`);
  // Attempt to reconnect automatically (handled by discord.js)
});

// Login to Discord
client.login(process.env.DISCORD_BOT_TOKEN)
  .then(() => console.log('Bot login initiated.'))
  .catch((error) => console.error('Failed to login:', error));