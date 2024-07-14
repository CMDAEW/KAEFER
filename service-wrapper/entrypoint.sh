#!/bin/bash

# Ensure the script exits if any command fails
set -e

_term() { 
  echo "Caught SIGTERM signal!" 
  kill -TERM "$backend_process" 2>/dev/null
  kill -TERM "$db_process" 2>/dev/null
  kill -TERM "$dbgate_process" 2>/dev/null
  kill -TERM "$xvfb_process" 2>/dev/null
  kill -TERM "$dbus_process" 2>/dev/null
}

trap _term SIGTERM

# Set environment variables
export DB_NAME=${DB_NAME:-invoicing}
export DB_USER=${DB_USER:-flaskuser}
export DB_PASSWORD=${DB_PASSWORD:-flaskpassword}
export DB_DUMP_FILE=${DB_DUMP_FILE:-/app/my_database_dump.sql}

echo "Starting Invoicing..."

# Ensure D-Bus is installed
if ! command -v dbus-daemon &> /dev/null
then
    echo "D-Bus is not installed. Installing..."
    apt-get update && apt-get install -y dbus
fi

# Start D-Bus daemon
echo "Starting D-Bus daemon..."
dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address --fork &
dbus_process=$!
DBUS_SESSION_BUS_ADDRESS=$(dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address)

# Export DBUS_SESSION_BUS_ADDRESS
export DBUS_SESSION_BUS_ADDRESS

# Start Xvfb
Xvfb :99 -screen 0 1024x768x16 &
xvfb_process=$!

echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Starting MariaDB server..."

# Ensure the data directory has the correct permissions
mkdir -p /var/lib/mysql /var/run/mysqld
chown -R mysql:mysql /var/lib/mysql /var/run/mysqld

# Initialize MariaDB data directory if empty
if [ -z "$(ls -A /var/lib/mysql)" ]; then
    echo "Initializing MariaDB data directory..."
    mysql_install_db --user=mysql --datadir=/var/lib/mysql
fi

# Start the MariaDB server as the mysql user
mysqld_safe --user=mysql --datadir=/var/lib/mysql &
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

# Check if the database exists; if not, create it and import the dump
DB_EXISTS=$(mysql -sse "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='$DB_NAME'")

if [ -z "$DB_EXISTS" ]; then
    echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Creating database $DB_NAME..."
    mysql -e "CREATE DATABASE $DB_NAME;"
    echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Creating user $DB_USER..."
    mysql -e "CREATE USER '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';"
    mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';"
    mysql -e "FLUSH PRIVILEGES;"
    echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Importing database dump..."
    mysql $DB_NAME < $DB_DUMP_FILE
else
    echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Database $DB_NAME already exists."
fi

echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Applying database migrations..."
flask db upgrade

# Start the backend process
echo "$(date +'%Y-%m-%dT%H:%M:%S%z') Starting Invoicing backend..."
gunicorn -b 0.0.0.0:5005 --worker-class gthread --workers 3 app:app &
backend_process=$!

wait $backend_process $db_process $dbgate_process $xvfb_process $dbus_process
