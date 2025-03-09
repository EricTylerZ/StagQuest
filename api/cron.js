const { get, put } = require('@vercel/blob');
const { sendPrompt } = require('../bot/discordBot');

module.exports = async (req, res) => {
  const times = ['Lauds', 'Prime', 'Terce', 'Sext', 'None', 'Vespers', 'Compline'];
  const now = new Date();
  const hour = now.getUTCHours();
  const timeIndex = Math.floor(hour / 3);
  const currentTime = times[timeIndex] || 'Compline';

  // Fetch all active novenas (simulate DB query with blob list)
  const { blobs } = await get({ prefix: 'novenas/' });
  const activeNovenas = blobs.filter(b => {
    const novena = JSON.parse(b.data);
    const daysElapsed = Math.floor((now - new Date(novena.start_time)) / (1000 * 60 * 60 * 24));
    return daysElapsed < 9;
  });

  for (const blob of activeNovenas) {
    const novena = JSON.parse(blob.data);
    const day = Math.min(Math.floor((now - new Date(novena.start_time)) / (1000 * 60 * 60 * 24)) + 1, 9);
    await sendPrompt(novena.stag_id, novena.owner_address, day, currentTime);
    if (currentTime === 'Compline') {
      novena.current_day = day + 1;
      await put(`novenas/${novena.stag_id}.json`, JSON.stringify(novena), { access: 'public' });
    }
  }
  res.status(200).send('Cron executed');
};