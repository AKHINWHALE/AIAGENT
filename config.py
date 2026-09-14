"""
config.py - Loads your secret keys and settings
This file reads your .env file and makes the keys available to other files
"""
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

class Config:
    # ========================================
    # OpenAI Settings (The Brain)
    # ========================================
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = "gpt-4o-mini"
    TEMPERATURE = 0.3
    
    # ========================================
    # Twilio Settings (WhatsApp Messages)
    # ========================================
    TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
    MY_WHATSAPP = os.getenv("MY_WHATSAPP_NUMBER")
    
    # ========================================
    # Tavily Settings (Internet Search)
    # ========================================
    TAVILY_KEY = os.getenv("TAVILY_API_KEY")
    
    # ========================================
    # Gmail Settings (Read Emails)
    # ========================================
    GMAIL_USER = os.getenv("GMAIL_USER")
    GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    
    # ========================================
    # Work Schedule Settings
    # ========================================
    WORK_START_HOUR = 7
    WORK_END_HOUR = 22
    APPROVAL_TIMEOUT = 3600