#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Function to handle SIGTERM signal
_term() { 
  echo "Caught SIGTERM signal!" 
  kill -TERM "$backend_process" 2>/dev/null
  kill -TERM "$db_process" 2>/dev/null
}

trap _term SIGTERM

# Set environment variables
export DB_NAME="invoicing"
export DB_USER="flaskuser"
export DB_PASSWORD="flaskpassword"
export DB_DUMP_FILE="/app/my_database_dump.sql"

echo "Starting Invoicing..."

# DATABASE SETUP

echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Starting MariaDB server..."

# Ensure the data directory has the correct permissions
mkdir -p /var/lib/mysql /var/run/mysqld
chown -R mysql:mysql /var/lib/mysql /var/run/mysqld

# Initialize MariaDB data directory if empty
if [ -z "$(ls -A /var/lib/mysql)" ]; then
    echo "Initializing MariaDB data directory..."
    mysql_install_db --user=mysql --datadir=/var/lib/mysql
fi

# Start the MariaDB server as the mysql user using the provided command
/usr/sbin/mysqld --user=mysql --datadir='/var/lib/mysql' --console --skip-networking=0 --bind-address=0.0.0.0 &
db_process=$!

# Wait for MariaDB to be ready
for i in {30..0}; do
    if mysqladmin ping -h localhost --silent; then
        break
    fi
    echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Waiting for database connection..."
    sleep 2
done

if [ "$i" = 0 ]; then
    echo "MariaDB did not start within the expected time. Check the MariaDB logs for more information."
    tail -n 50 /var/log/mysql/*.log
    exit 1
fi

echo "MariaDB is up and running."

# Create the database and user if they don't already exist
echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Setting up database and user..."
if ! mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"; then
    echo "Error creating database."
    exit 1
fi

if ! mysql -e "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';"; then
    echo "Error creating user."
    exit 1
fi

if ! mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';"; then
    echo "Error granting privileges."
    exit 1
fi

if ! mysql -e "FLUSH PRIVILEGES;"; then
    echo "Error flushing privileges."
    exit 1
fi

# Export environment variables for Flask
export FLASK_APP=app.py
export FLASK_ENV=production

# Start the Flask application using Gunicorn with increased timeout and appropriate worker configuration
echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Starting Flask application..."
exec gunicorn --preload --timeout 120 --workers 4 --threads 2 --bind 0.0.0.0:5005 app:app &
backend_process=$!

wait -n $backend_process $db_process
