const { get, put } = require('@vercel/blob');
const { sendPrompt } = require('../bot/discordBot');

module.exports = async (req, res) => {
  const times = {
    6: 'Lauds',   // 6 AM UTC
    8: 'Prime',   // 8 AM
    10: 'Terce',  // 10 AM
    12: 'Sext',   // 12 PM
    15: 'None',   // 3 PM
    18: 'Vespers', // 6 PM
    21: 'Compline' // 9 PM
  };
  const now = new Date();
  const hour = now.getUTCHours();
  const currentTime = times[hour] || null;
  if (!currentTime) return res.status(200).send('No prompt for this hour');

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