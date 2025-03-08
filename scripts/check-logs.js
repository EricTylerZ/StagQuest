const { exec } = require('child_process');
const fs = require('fs');

function checkVercelLogs() {
  exec('vercel inspect --logs stag-quest.vercel.app', (error, stdout, stderr) => {
    if (error) {
      console.error(`Error fetching logs: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Stderr: ${stderr}`);
      return;
    }
    // Parse logs (assuming logs are in stdout)
    const logs = stdout.split('\n');
    const errorLogs = logs.filter(log => log.includes('ERROR') && (log.includes('/api/mint') || log.includes('/api/status')));
    if (errorLogs.length > 0) {
      console.log('Found errors in Vercel logs:');
      console.log(errorLogs.join('\n'));
      fs.writeFileSync('vercel-errors.txt', errorLogs.join('\n'));
    } else {
      console.log('No API errors found in Vercel logs.');
    }
  });
}

checkVercelLogs();