# Use an official Ubuntu base image
FROM ubuntu:22.04

# Avoid warnings by switching to noninteractive for the build process
ENV DEBIAN_FRONTEND=noninteractive

ENV USER=root

# Updates packages
RUN apt-get update

# Install packages
RUN apt-get install -y python3 python3-pip 
RUN python3 -m venv /app
RUN /app/bin/pip install meshtastic prometheus_client

# clean up installers
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set the working directory in the container
WORKDIR /app

# Copy Bosmon
COPY mesh_exporter.py mesh_exporter.py
COPY start.sh start.sh
RUN chmod +x start.sh

HEALTHCHECK --interval=5s \
  CMD pgrep -f "mesh_exporter.py" || exit 1

ENTRYPOINT ["/app/start.sh"]
