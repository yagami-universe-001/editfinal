# Deployment Guide

This guide covers various deployment methods for the Video Encoder Bot.

## Table of Contents
- [Local Deployment](#local-deployment)
- [Docker Deployment](#docker-deployment)
- [VPS Deployment](#vps-deployment)
- [Heroku Deployment](#heroku-deployment)
- [Railway Deployment](#railway-deployment)

## Local Deployment

### Prerequisites
- Python 3.9 or higher
- FFmpeg
- MongoDB

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/telegram-video-encoder-bot.git
cd telegram-video-encoder-bot
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
nano .env
```

5. **Start MongoDB**
```bash
sudo systemctl start mongod
```

6. **Run the bot**
```bash
python bot.py
```

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/telegram-video-encoder-bot.git
cd telegram-video-encoder-bot
```

2. **Configure environment**
```bash
cp .env.example .env
nano .env
```

3. **Build and run**
```bash
docker-compose up -d
```

4. **View logs**
```bash
docker-compose logs -f bot
```

5. **Stop the bot**
```bash
docker-compose down
```

### Update Bot
```bash
docker-compose down
git pull
docker-compose up -d --build
```

## VPS Deployment (Ubuntu/Debian)

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Dependencies
```bash
# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install FFmpeg
sudo apt install ffmpeg -y

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -sc)/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install mongodb-org -y
sudo systemctl start mongod
sudo systemctl enable mongod

# Install Git
sudo apt install git -y
```

### 3. Setup Bot
```bash
# Clone repository
git clone https://github.com/yourusername/telegram-video-encoder-bot.git
cd telegram-video-encoder-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env
```

### 4. Create Systemd Service
```bash
sudo nano /etc/systemd/system/video-bot.service
```

Add this content:
```ini
[Unit]
Description=Video Encoder Bot
After=network.target mongodb.service

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/telegram-video-encoder-bot
ExecStart=/path/to/telegram-video-encoder-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5. Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl start video-bot
sudo systemctl enable video-bot
sudo systemctl status video-bot
```

### 6. View Logs
```bash
sudo journalctl -u video-bot -f
```

## Heroku Deployment

### Prerequisites
- Heroku account
- Heroku CLI

### Steps

1. **Create Heroku app**
```bash
heroku login
heroku create your-bot-name
```

2. **Add buildpacks**
```bash
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
```

3. **Add MongoDB addon**
```bash
heroku addons:create mongolab:sandbox
```

4. **Set environment variables**
```bash
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set ADMINS=123456789
# Add other variables from .env
```

5. **Create Procfile**
```bash
echo "worker: python bot.py" > Procfile
```

6. **Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

7. **Scale worker**
```bash
heroku ps:scale worker=1
```

## Railway Deployment

### Steps

1. **Fork the repository** on GitHub

2. **Go to Railway.app** and sign in

3. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your forked repository

4. **Add MongoDB**
   - Click "New"
   - Select "Database"
   - Choose "MongoDB"

5. **Configure Environment Variables**
   - Go to your bot service
   - Click "Variables"
   - Add all variables from `.env.example`
   - Use the MongoDB connection string from the MongoDB service

6. **Deploy**
   - Railway will automatically deploy your bot
   - View logs in the "Deployments" tab

## Environment Variables

Required variables:
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
DB_URI=mongodb://localhost:27017
ADMINS=123456789,987654321
```

Optional variables:
```env
DEFAULT_PRESET=medium
DEFAULT_CODEC=libx264
DEFAULT_AUDIO_BITRATE=128k
DEFAULT_CRF=23
MAX_FILE_SIZE=2147483648
MAX_FILE_SIZE_PREMIUM=4294967296
MAX_CONCURRENT_TASKS=2
WORKERS=4
```

## Monitoring and Maintenance

### Check Bot Status
```bash
# Local/VPS
sudo systemctl status video-bot

# Docker
docker-compose ps

# Heroku
heroku ps

# Railway
Check dashboard
```

### View Logs
```bash
# Local/VPS
sudo journalctl -u video-bot -f

# Docker
docker-compose logs -f bot

# Heroku
heroku logs --tail

# Railway
Check "Deployments" tab
```

### Update Bot
```bash
# Local/VPS
cd telegram-video-encoder-bot
git pull
sudo systemctl restart video-bot

# Docker
docker-compose down
git pull
docker-compose up -d --build

# Heroku
git pull
git push heroku main

# Railway
Git push to your repo, Railway auto-deploys
```

### Backup Database
```bash
# MongoDB backup
mongodump --out=/path/to/backup

# Restore
mongorestore /path/to/backup
```

## Troubleshooting

### Bot not starting
- Check logs for errors
- Verify environment variables
- Ensure MongoDB is running
- Check FFmpeg installation

### Encoding fails
- Verify FFmpeg is properly installed
- Check available disk space
- Review encoding settings
- Check file permissions

### Database connection errors
- Verify MongoDB is running
- Check DB_URI in .env
- Ensure proper network connectivity

### Out of memory
- Reduce MAX_CONCURRENT_TASKS
- Increase server RAM
- Implement queue system properly

## Security Best Practices

1. **Never commit .env file**
2. **Use strong MongoDB passwords in production**
3. **Enable firewall on VPS**
4. **Regularly update dependencies**
5. **Monitor bot for abuse**
6. **Implement rate limiting**
7. **Use HTTPS for webhook (if using)**

## Support

For issues and questions:
- Create an issue on GitHub
- Join support group: [Your Support Group]
- Email: [your-email@example.com]
