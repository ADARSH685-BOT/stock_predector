"""
Author: Akshat Singh
GitHub: @akshatsingh-dev
Email: akshat@example.com
Date: 2025-07-25
Role: Developer
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Stock symbols to monitor
    SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA']
    
    # Data collection settings
    UPDATE_INTERVAL = 60  # seconds
    PREDICTION_HORIZON = 30  # minutes
    LOOKBACK_PERIOD = 100  # data points for prediction
    
    # Model settings
    MODEL_RETRAIN_INTERVAL = 24  # hours
    PREDICTION_THRESHOLD = 0.02  # 2% change threshold for notifications
    
    # Notification settings
    EMAIL_ENABLED = True
    SMS_ENABLED = True
    PUSH_ENABLED = True
    
    # Email configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
    
    # Twilio configuration for SMS
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    RECIPIENT_PHONE = os.getenv('RECIPIENT_PHONE')
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))
    
    # Data storage
    DATA_DIR = 'data'
    MODELS_DIR = 'models'
    
    # API settings
    API_DELAY = 0.1  # seconds between API calls to avoid rate limiting
