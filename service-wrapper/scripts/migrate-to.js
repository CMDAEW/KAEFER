const { exec } = require("child_process");

module.exports = async function toMigration() {
  console.log("Running to migration script");

  // Set necessary environment variables
  process.env.FLASK_APP = 'app.py';  // or 'app:app' if it's in a package
  process.env.FLASK_ENV = 'production';

  // Run the Flask-Migrate command
  await new Promise((resolve, reject) => {
    exec("flask db upgrade", (error, stdout, stderr) => {
      if (error) {
        console.error(`Migration error: ${stderr}`);
        reject(error);
      } else {
        console.log(`Migration output: ${stdout}`);
        resolve();
      }
    });
  }).catch(error => {
    console.error('Migration failed:', error);
    process.exit(1);
  });
};
