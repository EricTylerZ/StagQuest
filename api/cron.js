const { get, put } = require('@vercel/blob');

module.exports = async (req, res) => {
  const times = { 'Matins': 2.5, 'Lauds': 6, 'Terce': 9, 'Sext': 12, 'None': 15, 'Vespers': 18, 'Compline': 21 };
  try {
    const { blobs } = await get({ prefix: 'novenas/' });
    for (const blob of blobs) {
      const novena = JSON.parse(blob.data);
      const utcOffset = parseInt(novena.timezone);
      const userTime = new Date(new Date().getTime() + utcOffset * 60 * 60 * 1000);
      const hour = userTime.getHours() + userTime.getMinutes() / 60;
      const currentTime = Object.keys(times).find(t => Math.abs(hour - times[t]) < 1) || null;

      if (currentTime) {
        const daysElapsed = Math.floor((userTime - new Date(novena.start_time)) / (1000 * 60 * 60 * 24));
        if (daysElapsed < 9 && novena.current_day <= daysElapsed + 1) {
          // Bot handles DMs, just update day if needed
          if (currentTime === 'Compline') {
            novena.current_day = Math.min(daysElapsed + 1, 9);
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