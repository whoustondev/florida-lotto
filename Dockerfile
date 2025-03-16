# Use the official Python image
FROM python:3.12-bookworm

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Set the application directory
ENV APP_HOME /back-end
WORKDIR $APP_HOME
COPY . ./

# Install dependencies
RUN apt-get update && apt-get install -y wget unzip curl \
    && wget -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_124.0.6367.91-1_amd64.deb \
    && dpkg -i /tmp/google-chrome-stable_current_amd64.deb || apt-get install -fy \
    && rm -rf /tmp/google-chrome-stable_current_amd64.deb \
    && wget -O /tmp/chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.91/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver-linux64.zip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for Cloud Run
ENV PORT 5000
EXPOSE 5000
# Start the application using Gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 1 --timeout 0 --log-level debug app:app
