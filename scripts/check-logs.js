// scripts/check-logs.js
const { exec } = require('child_process');
const fs = require('fs');

function checkVercelLogs() {
  exec('vercel logs stag-quest.vercel.app --json', (error, stdout, stderr) => {
    if (error) {
      console.error(`Error fetching logs: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Stderr: ${stderr}`);
      return;
    }
    const logs = JSON.parse(stdout);
    const errorLogs = logs.filter(log => log.type === 'error' && (log.message.includes('/api/mint') || log.message.includes('/api/status')));
    if (errorLogs.length > 0) {
      console.log('Found errors in Vercel logs:');
      console.log(JSON.stringify(errorLogs, null, 2));
      fs.writeFileSync('vercel-errors.json', JSON.stringify(errorLogs, null, 2));
    } else {
      console.log('No API errors found in Vercel logs.');
    }
  });
}

checkVercelLogs();