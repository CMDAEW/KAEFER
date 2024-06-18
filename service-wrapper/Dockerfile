# Use your custom base image
FROM cmuede/start9-invoicing-app:0.1.0

# Install necessary packages and yq
RUN apt-get update && apt-get install -y wget curl sudo bash tini \
    && wget https://github.com/mikefarah/yq/releases/download/v4.25.1/yq_linux_arm.tar.gz -O - |\
        tar xz && mv yq_linux_arm /usr/bin/yq \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV APP_HOST invoicing.embassy
ENV APP_PORT 12596
ENV TOR_PROXY_IP embassy
ENV TOR_PROXY_PORT 9050

# Copy requirements.txt and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Add scripts and make them executable
ADD ./entrypoint.sh /usr/local/bin/entrypoint.sh
ADD check-web.sh /usr/local/bin/check-web.sh
RUN chmod a+x /usr/local/bin/entrypoint.sh
RUN chmod a+x *.sh

# Set entrypoint
ENTRYPOINT ["tini", "--", "/usr/local/bin/entrypoint.sh"]