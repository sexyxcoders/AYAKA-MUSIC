# Use python 3.10 + node 19 on Debian Bullseye (not old Buster)
FROM nikolaik/python-nodejs:python3.10-nodejs19-bullseye

# Install required packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg aria2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/
WORKDIR /app/

# Upgrade pip and install Python dependencies
RUN python -m pip install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt

# Start command
CMD ["bash", "start"]
