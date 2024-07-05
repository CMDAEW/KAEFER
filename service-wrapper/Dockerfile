# Use your custom base image
FROM cmuede/invoicing-app:0.3.0

# Install necessary packages and yq
RUN apt-get update && apt-get install -y wget curl sudo bash tini mariadb-server \
    && wget https://github.com/mikefarah/yq/releases/download/v4.25.1/yq_linux_arm.tar.gz -O - |\
        tar xz && mv yq_linux_arm /usr/bin/yq \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables using key=value format
ENV APP_HOST=invoicing.embassy
ENV APP_PORT=5005
ENV TOR_PROXY_IP=embassy
ENV TOR_PROXY_PORT=9050
ENV DB_HOST=localhost
ENV DB_PORT=3306
ENV DB_USER=flaskuser
ENV DB_PASSWORD=flaskpassword
ENV DB_NAME=invoicing

# Copy requirements.txt and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Ensure the MySQL data directory and run directory have the correct permissions
RUN mkdir -p /var/lib/mysql /var/run/mysqld && chown -R mysql:mysql /var/lib/mysql /var/run/mysqld

# Copy the database dump file into the container
COPY my_database_dump.sql /invoice/my_database_dump.sql

# Add scripts and make them executable
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod a+x /usr/local/bin/entrypoint.sh

# Expose the Flask port
EXPOSE 5005

# Set the entrypoint to use Tini
ENTRYPOINT ["tini", "--", "/usr/local/bin/entrypoint.sh"]
