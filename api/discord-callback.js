const { put } = require('@vercel/blob');

module.exports = async (req, res) => {
  console.log('Discord callback hit with query:', req.query); // Debug
  const { code } = req.query;
  if (!code) {
    console.error('No code provided');
    return res.status(400).json({ error: 'No code provided' });
  }

  const clientId = process.env.DISCORD_CLIENT_ID;
  const clientSecret = process.env.DISCORD_CLIENT_SECRET;
  const redirectUri = 'https://stag-quest.vercel.app/api/discord-callback';

  try {
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
    if (!tokenData.access_token) {
      console.error('Failed to get access token:', tokenData);
      return res.status(500).json({ error: 'Failed to get access token' });
    }

    const userResponse = await fetch('https://discord.com/api/users/@me', {
      headers: { Authorization: `Bearer ${tokenData.access_token}` },
    });
    const userData = await userResponse.json();
    console.log('User data:', userData);

    const discordId = userData.id;
    const mapping = { stagIds: [], timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC', email: '' };
    await put(`discord_mappings/${discordId}.json`, JSON.stringify(mapping), { access: 'public' });

    console.log('Redirecting to:', `https://stag-quest.vercel.app/?discordId=${discordId}`);
    res.redirect(`https://stag-quest.vercel.app/?discordId=${discordId}`);
  } catch (error) {
    console.error('OAuth error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};