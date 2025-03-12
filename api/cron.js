const { get, put } = require('@vercel/blob');
const { sendPrompt } = require('../bot/discordBot');

module.exports = async (req, res) => {
  const times = { 'Matins': 2.5, 'Lauds': 6, 'Terce': 9, 'Sext': 12, 'None': 15, 'Vespers': 18, 'Compline': 21 };
  try {
    const { blobs } = await get({ prefix: 'novenas/' });
    for (const blob of blobs) {
      const novena = JSON.parse(blob.data);
      const userTime = new Date().toLocaleString('en-US', { timeZone: novena.timezone });
      const hour = parseFloat(userTime.split(':')[0]) + (parseInt(userTime.split(':')[1]) / 60);
      const currentTime = Object.keys(times).find(t => Math.abs(hour - times[t]) < 1) || null;

      if (currentTime) {
        const daysElapsed = Math.floor((new Date() - new Date(novena.start_time)) / (1000 * 60 * 60 * 24));
        if (daysElapsed < 9) {
          const day = Math.min(daysElapsed + 1, 9);
          await sendPrompt(novena.stag_id, novena.discord_id, day, currentTime);
          if (currentTime === 'Compline') {
            novena.current_day = day + 1;
            await put(`novenas/${novena.stag_id}.json`, JSON.stringify(novena), { access: 'public' });
          }
        }
      }
    }
    res.status(200).send('Cron executed successfully');
  } catch (error) {
    console.error('Error in cron job:', error);
    res.status(500).send('Error executing cron job');
  }
};