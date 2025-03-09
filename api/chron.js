const { Pool } = require('pg');
const { sendPrompt } = require('../bot/discordBot');

const pool = new Pool({ connectionString: process.env.POSTGRES_URL });

module.exports = async (req, res) => {
  const times = ['Lauds', 'Prime', 'Terce', 'Sext', 'None', 'Vespers', 'Compline'];
  const now = new Date();
  const hour = now.getUTCHours();
  const timeIndex = Math.floor(hour / 3); // Rough 3-hour spacing
  const currentTime = times[timeIndex] || 'Compline';

  const { rows } = await pool.query('SELECT * FROM novenas WHERE start_time <= NOW() - INTERVAL \'9 days\' IS NOT TRUE');
  for (const novena of rows) {
    const day = Math.min(Math.floor((now - new Date(novena.start_time)) / (1000 * 60 * 60 * 24)) + 1, 9);
    await sendPrompt(novena.stag_id, novena.owner_address, day, currentTime);
    if (currentTime === 'Compline') {
      await pool.query('UPDATE novenas SET current_day = $1 WHERE stag_id = $2', [day + 1, novena.stag_id]);
    }
  }
  res.status(200).send('Cron executed');
};