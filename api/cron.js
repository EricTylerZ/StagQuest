const { get, put } = require('@vercel/blob');
const { sendPrompt } = require('../bot/discordBot');

module.exports = async (req, res) => {
  const { stagId } = req.query; // Optional: Trigger specific Stag
  const times = { 'Matins': 2.5, 'Lauds': 6, 'Terce': 9, 'Sext': 12, 'None': 15, 'Vespers': 18, 'Compline': 21 };

  const { blobs: mappings } = await get({ prefix: 'discord_mappings/' });
  for (const mappingBlob of mappings) {
    const mapping = JSON.parse(mappingBlob.data);
    const discordId = mappingBlob.pathname.split('/')[1].replace('.json', '');
    const userTime = new Date().toLocaleString('en-US', { timeZone: mapping.timezone });
    const hour = parseFloat(userTime.split(':')[0]) + (parseInt(userTime.split(':')[1]) / 60);
    const currentTime = Object.keys(times).find(t => Math.abs(hour - times[t]) < 1) || null;

    for (const stagId of mapping.stagIds) {
      const { data } = await get(`novenas/${stagId}.json`);
      let novena = data ? JSON.parse(data) : null;

      if (!novena && req.query.stagId === stagId.toString()) {
        // Initial novena start
        novena = { stag_id: stagId, owner_address: discordId, start_time: new Date().toISOString(), current_day: 1, responses: {} };
        await put(`novenas/${stagId}.json`, JSON.stringify(novena), { access: 'public' });
        await sendPrompt(stagId, discordId, 1, currentTime || 'None');
      } else if (novena) {
        const daysElapsed = Math.floor((new Date() - new Date(novena.start_time)) / (1000 * 60 * 60 * 24));
        if (daysElapsed < 9 && currentTime) {
          const day = Math.min(daysElapsed + 1, 9);
          await sendPrompt(stagId, discordId, day, currentTime);
          if (currentTime === 'Compline') {
            novena.current_day = day + 1;
            await put(`novenas/${stagId}.json`, JSON.stringify(novena), { access: 'public' });
          }
        }
      }
    }
  }
  res.status(200).send('Cron executed');
};