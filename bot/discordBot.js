const { Client, GatewayIntentBits } = require('discord.js');
const { get, put } = require('@vercel/blob');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.DirectMessages,
  ],
});

client.on('ready', () => {
  console.log('Bot is ready!');
});

client.on('messageCreate', async (message) => {
  if (message.author.bot) return;
  console.log('Received message from', message.author.id, ':', message.content);

  try {
    if (message.content.startsWith('!')) {
      // Handle commands (e.g., !help)
    } else {
      // Handle novena responses
      const userId = message.author.id;
      // Placeholder logic for novena processing
      // Replace with actual novena lookup and response handling later
      message.reply('Your response has been recorded.');
    }
  } catch (error) {
    console.error('Error handling message:', error);
    message.reply('An error occurred while processing your response.');
  }
});

client.login(process.env.DISCORD_BOT_TOKEN);