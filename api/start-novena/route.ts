import { put } from '@vercel/blob';
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { stagId, ownerAddress, timezone, discordId, email, preferredChannel } = await request.json();

  if (!stagId || !ownerAddress || !timezone || !preferredChannel) {
    return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
  }

  const novena = {
    stag_id: Number(stagId),
    owner_address: ownerAddress,
    discord_id: discordId || '',
    email: email || '',
    start_time: new Date().toISOString(),
    current_day: 1,
    responses: {},
    timezone,
    preferred_channel: preferredChannel,
  };

  try {
    await put(`novenas/${stagId}.json`, JSON.stringify(novena), {
      access: 'public',
      token: process.env.BLOB_READ_WRITE_TOKEN,
    });
    return NextResponse.json({ message: 'Novena started' }, { status: 200 });
  } catch (error) {
    console.error('Error starting novena:', error);
    return NextResponse.json({ error: 'Failed to start novena' }, { status: 500 });
  }
}