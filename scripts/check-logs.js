const { exec } = require('child_process');
const fs = require('fs');

function checkVercelLogs() {
  // Fetch build logs
  exec('vercel inspect --logs stag-quest.vercel.app', (error, stdout, stderr) => {
    if (error) {
      console.error(`Error fetching build logs: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Stderr (build logs): ${stderr}`);
      return;
    }
    const buildLogs = stdout.split('\n');
    const buildErrors = buildLogs.filter(log => log.includes('ERROR'));
    if (buildErrors.length > 0) {
      console.log('Found errors in Vercel build logs:');
      console.log(buildErrors.join('\n'));
      fs.writeFileSync('vercel-build-errors.txt', buildErrors.join('\n'));
    } else {
      console.log('No errors found in Vercel build logs.');
    }
  });

  // Fetch runtime logs for the last 10 minutes
  exec('vercel logs stag-quest.vercel.app --since=10m', (error, stdout, stderr) => {
    if (error) {
      console.error(`Error fetching runtime logs: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Stderr (runtime logs): ${stderr}`);
      return;
    }
    const runtimeLogs = stdout.split('\n');
    const apiErrors = runtimeLogs.filter(log => log.includes('ERROR') && log.includes('/api/status'));
    if (apiErrors.length > 0) {
      console.log('Found errors in Vercel runtime logs:');
      console.log(apiErrors.join('\n'));
      fs.writeFileSync('vercel-runtime-errors.txt', apiErrors.join('\n'));
    } else {
      console.log('No API errors found in Vercel runtime logs.');
    }
  });
}

checkVercelLogs();