import { put } from '@vercel/blob';
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { stagId, ownerAddress, discordId, email, utcOffset, preferredChannel } = await request.json();

  if (!stagId || !ownerAddress) {
    return NextResponse.json({ error: 'Missing stagId or ownerAddress' }, { status: 400 });
  }

  const metadata = {
    stagId: Number(stagId),
    ownerAddress,
    discordId: discordId || '',
    email: email || '',
    utcOffset: utcOffset || '-7',
    preferredChannel: preferredChannel || 'discord',
  };

  try {
    await put(`stags/${stagId}.json`, JSON.stringify(metadata), {
      access: 'public',
      token: process.env.BLOB_READ_WRITE_TOKEN,
    });
    return NextResponse.json({ message: 'Metadata saved successfully' }, { status: 200 });
  } catch (error) {
    console.error('Error saving metadata:', error);
    return NextResponse.json({ error: 'Failed to save metadata' }, { status: 500 });
  }
}