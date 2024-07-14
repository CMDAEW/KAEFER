FROM cmuede/invoicing-app:2.5.0

# Install necessary packages including DbGate and required libraries
RUN apt-get update && apt-get install -y wget curl sudo bash tini mariadb-server dbus-x11 \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libgdk-pixbuf2.0-0 libgtk-3-0 libcairo2 libpango1.0-0 \
    libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 libdrm2 libgbm1 \
    libasound2 libcups2 libxshmfence1 libnspr4 libwayland-client0 libwayland-cursor0 libwayland-egl1 \
    libxi6 libxtst6 libxinerama1 libxkbcommon0 libxss1 xvfb \
    && wget https://github.com/mikefarah/yq/releases/download/v4.25.1/yq_linux_arm.tar.gz -O - |\
        tar xz && mv yq_linux_arm /usr/bin/yq \
    && wget https://github.com/dbgate/dbgate/releases/download/v5.3.1/dbgate-5.3.1-linux_x64.tar.gz -O - |\
        tar xz -C /usr/local/bin/ --strip-components=1 \
    && chmod +x /usr/local/bin/dbgate \
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
ENV DBGATE_NO_UPDATE=1
ENV ELECTRON_ENABLE_LOGGING=1
ENV ELECTRON_DISABLE_GPU=1
ENV QT_QPA_PLATFORM=offscreen
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null
ENV DISPLAY=:99

# Add scripts and make them executable
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod a+x /usr/local/bin/entrypoint.sh

# Expose necessary ports
EXPOSE 5005
EXPOSE 3000

# Set entrypoint
ENTRYPOINT ["tini", "--", "/usr/local/bin/entrypoint.sh"]
