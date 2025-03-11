const { put } = require('@vercel/blob');

module.exports = async (req, res) => {
  const { code } = req.query;
  if (!code) return res.status(400).json({ error: 'No code provided' });

  const clientId = process.env.DISCORD_CLIENT_ID;
  const clientSecret = process.env.DISCORD_CLIENT_SECRET;
  const redirectUri = 'https://stag-quest.vercel.app/api/discord-callback';

  const tokenResponse = await fetch('https://discord.com/api/oauth2/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      grant_type: 'authorization_code',
      code,
      redirect_uri: redirectUri,
    }),
  });

  const tokenData = await tokenResponse.json();
  if (!tokenData.access_token) return res.status(500).json({ error: 'Failed to get access token' });

  const userResponse = await fetch('https://discord.com/api/users/@me', {
    headers: { Authorization: `Bearer ${tokenData.access_token}` },
  });
  const userData = await userResponse.json();

  const discordId = userData.id;
  const mapping = { stagIds: [], timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC' };
  await put(`discord_mappings/${discordId}.json`, JSON.stringify(mapping), { access: 'public' });

  res.redirect(`/app?page=discordId=${discordId}`);
};