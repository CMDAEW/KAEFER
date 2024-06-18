#!/bin/bash

# Ensure the script exits if any command fails
set -ea

echo "Starting Invoicing..."

# Export environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Wait for dependencies to be ready (optional, if your app relies on other services like a database)
# You can use a tool like wait-for-it or add custom checks here
./wait-for-it.sh db:5432 -- echo "Database is up"

# Run database migrations (if any)
# Uncomment and modify the command below to run your migrations
flask db upgrade

# Start the Flask application using gunicorn
exec gunicorn --bind 0.0.0.0:12596 app:app
