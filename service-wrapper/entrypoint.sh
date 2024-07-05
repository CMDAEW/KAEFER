#!/bin/bash

# Ensure the script exits if any command fails
set -e

_term() { 
  echo "Caught SIGTERM signal!" 
  kill -TERM "$backend_process" 2>/dev/null
  kill -TERM "$db_process" 2>/dev/null
}

# Set environment variables
export DB_NAME="invoicing"
export DB_USER="flaskuser"
export DB_PASSWORD="flaskpassword"

echo "Starting Invoicing..."

# DATABASE SETUP

echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Starting MariaDB server..."

# Start the MariaDB server as the mysql user
mysqld_safe --user=mysql &
db_process=$!

# Wait for MariaDB to be ready
until mysqladmin ping -h localhost --silent; do
    echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Waiting for database connection..."
    sleep 2
done

# Check if the database exists; if not, create it
DB_EXISTS=$(mysql -sse "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='$DB_NAME'")

if [ -z "$DB_EXISTS" ]; then
    echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Creating database $DB_NAME..."
    mysql -e "CREATE DATABASE $DB_NAME;"
    echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Creating user $DB_USER..."
    mysql -e "CREATE USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';"
    echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Granting privileges to user $DB_USER on database $DB_NAME..."
    mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';"
    mysql -e "FLUSH PRIVILEGES;"
else
    echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Database $DB_NAME already exists."
fi

echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Starting Invoicing..."

# Export environment variables for Flask
export FLASK_APP=app.py
export FLASK_ENV=production

# Start the Flask application using gunicorn
exec tini -- gunicorn --bind 0.0.0.0:5005 app:app &
backend_process=$!

wait -n $backend_process $db_process
