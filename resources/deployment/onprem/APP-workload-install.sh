#!/bin/bash

# bring down necessary utilities
sudo yum install git java-17-openjdk-devel maven -y

# setup firewall rules
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# backup firewall rules
sudo cp /etc/firewalld/direct.xml /etc/firewalld/direct.xml.backup

# Stop and disable Apache if it is running (from a prior PHP-based deployment)
if systemctl is-active --quiet httpd; then
    sudo systemctl stop httpd
    sudo systemctl disable httpd
fi

# Allow Java to bind to port 80
sudo setcap 'cap_net_bind_service=+ep' $(readlink -f $(which java))

# Build the Spring Boot application
cd TechExcel-Migrate-Linux-workloads/resources/deployment/onprem/webapp
mvn package -DskipTests

# Install the app as a systemd service
APP_JAR=$(ls target/orders-*.jar | head -1)
APP_DIR=$(pwd)

sudo tee /etc/systemd/system/orders.service > /dev/null <<EOF
[Unit]
Description=Terra Firm Orders Application
After=network.target

[Service]
User=root
ExecStart=/usr/bin/java -jar ${APP_DIR}/${APP_JAR}
SuccessExitStatus=143
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Start and enable the service
sudo systemctl daemon-reload
sudo systemctl start orders
sudo systemctl enable orders

# Let the user know we are good
status=$?
[ $status -eq 0 ] && echo "The script was successful"
exit 0