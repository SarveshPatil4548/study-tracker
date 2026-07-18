# Study Tracker

A simple Flask web app to track your study sessions.

## Prerequisites

- Python 3.8+
- MySQL Server 8.0+ (or MariaDB 10.5+)

### Install MySQL

**Windows:**
Download and install from [MySQL Community Downloads](https://dev.mysql.com/downloads/mysql/). Choose the "MySQL Installer" for Windows.

**macOS:**
```bash
brew install mysql
brew services start mysql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

### Create Database and User

Log into MySQL and run:

```sql
CREATE DATABASE study_tracker;
CREATE USER 'study_user'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON study_tracker.* TO 'study_user'@'localhost';
FLUSH PRIVILEGES;
```

## Setup

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env
# Edit .env with your MySQL credentials

# Run the app
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_USER` | `root` | MySQL username |
| `DB_PASSWORD` | (empty) | MySQL password |
| `DB_HOST` | `localhost` | MySQL host |
| `DB_PORT` | `3306` | MySQL port |
| `DB_NAME` | `study_tracker` | Database name |
