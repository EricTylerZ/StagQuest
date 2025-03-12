const { Client, GatewayIntentBits } = require('discord.js');
const { get, put } = require('@vercel/blob');

const client = new Client({
  intents: [GatewayIntentBits.DirectMessages],
});

let isReady = false;

client.once('ready', () => {
  console.log(`Bot is online as ${client.user.tag} for cron!`);
  isReady = true;
});

client.login(process.env.DISCORD_BOT_TOKEN).catch(error => console.error('Cron bot login failed:', error));

module.exports = async (req, res) => {
  if (!isReady) {
    console.log('Bot not ready yet, waiting...');
    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for bot to be ready
    if (!isReady) return res.status(503).json({ error: 'Bot not ready' });
  }

  const times = { 'Matins': 2.5, 'Lauds': 6, 'Terce': 9, 'Sext': 12, 'None': 15, 'Vespers': 18, 'Compline': 21 };
  try {
    const { blobs } = await get({ prefix: 'novenas/' });
    if (!blobs || blobs.length === 0) {
      console.log('No novenas found in Blob storage.');
      return res.status(200).send('No novenas to process');
    }

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
          console.log(`Sent DM to ${novena.discord_id} for stag ${novena.stag_id}, day ${novena.current_day}`);

          if (currentTime === 'Compline') {
            novena.current_day = Math.min(daysElapsed + 1, 9);
            await put(`novenas/${novena.stag_id}.json`, JSON.stringify(novena), { access: 'public' });
            console.log(`Updated novena ${novena.stag_id} to day ${novena.current_day}`);
          }
        } catch (error) {
          console.error(`Failed to send DM for stag ${novena.stag_id}:`, error);
        }
      }
    }
    res.status(200).send('Cron executed successfully');
  } catch (error) {
    console.error('Error in cron job:', error);
    res.status(500).send('Error executing cron job');
  }
};