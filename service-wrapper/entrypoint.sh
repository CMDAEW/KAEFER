#!/bin/bash

# Ensure the script exits if any command fails
set -e

_term() { 
  echo "Caught SIGTERM signal!" 
  kill -TERM "$backend_process" 2>/dev/null
  kill -TERM "$db_process" 2>/dev/null
}

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

DB_NAME="invoicing"
DB_USER="flaskuser"
DB_PASSWORD="flaskpassword"

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

# Check if necessary environment variables are set
: "${DB_HOST:=localhost}"
: "${DB_PORT:=3306}"
: "${DB_USER:?Environment variable DB_USER not set}"
: "${DB_PASSWORD:?Environment variable DB_PASSWORD not set}"

# Export environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Maximum time to wait for MySQL (in seconds)
MAX_WAIT=120
WAIT_INTERVAL=3
WAIT_TIME=0

# Wait for the MySQL database to be available
while ! mysql -h"${DB_HOST}" -P"${DB_PORT}" -u"${DB_USER}" -p"${DB_PASSWORD}" -e "SHOW DATABASES;" > /dev/null 2>&1; do
    if [ $WAIT_TIME -ge $MAX_WAIT ]; then
        echo "$(date +'%Y-%m-%dT%H:%M:%S%z') MySQL is still unavailable after $MAX_WAIT seconds - exiting"
        exit 1
    fi
    echo "$(date +'%Y-%m-%dT%H:%M:%S%z') MySQL is unavailable - sleeping"
    sleep $WAIT_INTERVAL
    WAIT_TIME=$((WAIT_TIME + WAIT_INTERVAL))
done

echo "$(date +'%Y-%m-%dT%H:%M:%S%z') MySQL is up - executing command"

# Run database migrations (if any)
flask db upgrade

# Start the Flask application using gunicorn
exec gunicorn --bind 0.0.0.0:12596 app:app &
backend_process=$!

# SIGTERM HANDLING
trap _term SIGTERM

wait -n $db_process $backend_process

echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Verifying MySQL process..."
ps aux | grep mysqld

echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Checking MySQL logs..."
tail -n 50 /var/log/mysql/error.log
