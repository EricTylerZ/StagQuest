const { put } = require('@vercel/blob');

module.exports = async (req, res) => {
  const { stagId, ownerAddress, timezone, discordId, email } = req.body;

  console.log('Received start-novena request:', req.body);

  if (!stagId || !ownerAddress || !timezone || !discordId) {
    console.error('Missing required fields:', { stagId, ownerAddress, timezone, discordId });
    return res.status(400).json({ error: 'Missing stagId, ownerAddress, timezone, or discordId' });
  }

  const novena = {
    stag_id: Number(stagId),
    owner_address: ownerAddress,
    discord_id: discordId,
    email: email || '',
    start_time: new Date().toISOString(),
    current_day: 1,
    responses: {},
    timezone
  };

  try {
    await put(`novenas/${stagId}.json`, JSON.stringify(novena), { 
      access: 'public',
      token: process.env.BLOB_READ_WRITE_TOKEN // Add this from Vercel env vars
    });
    console.log(`Stored novena/${stagId}.json:`, novena);

    const mapping = { stagIds: [Number(stagId)], timezone, email: email || '' };
    await put(`discord_mappings/${discordId}.json`, JSON.stringify(mapping), { 
      access: 'public',
      token: process.env.BLOB_READ_WRITE_TOKEN
    });
    console.log(`Stored discord_mappings/${discordId}.json:`, mapping);

    res.status(200).json({ message: 'Novena started' });
  } catch (error) {
    console.error('Error starting novena:', error);
    res.status(500).json({ error: 'Failed to start novena' });
  }
};