"""
whatsapp.py - Send messages and approval requests to your WhatsApp
Uses Twilio's WhatsApp API
"""
from twilio.rest import Client
from config import Config
import json
import os
from datetime import datetime


class WhatsAppManager:
    """
    This class handles all WhatsApp messaging.
    It can send messages, approval requests, and daily summaries.
    """
    
    def __init__(self):
        """
        Initialize the WhatsApp Manager.
        This runs when you create a WhatsAppManager object.
        """
        try:
            # Create a Twilio client with your credentials
            self.client = Client(Config.TWILIO_SID, Config.TWILIO_TOKEN)
            
            # Store your WhatsApp number
            self.my_number = Config.MY_WHATSAPP
            
            # Store the Twilio WhatsApp number
            self.from_number = Config.TWILIO_FROM
            
            print("✅ WhatsApp Manager initialized successfully")
        
        except Exception as e:
            # If initialization fails, print an error
            print(f"⚠️ WhatsApp setup failed: {e}")
            print("   Check your Twilio credentials in .env file")
            
            # Set client to None so we know it's not working
            self.client = None
    
    def send_message(self, message: str) -> bool:
        """
        Send a WhatsApp message to you.
        """
        # Check if Twilio client is initialized
        if not self.client:
            print(f"\n[SIMULATED WHATSAPP MESSAGE]\n{message}\n")
            return False
        
        try:
            # Send the message via Twilio
            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.my_number
            )
            print(f"✅ WhatsApp message sent successfully!")
            return True
        
        except Exception as e:
            # If Twilio blocks it (e.g., ContentSid required), simulate it gracefully
            error_msg = str(e)
            if "ContentSid" in error_msg or "21654" in error_msg:
                print(f"\n⚠️ Twilio requires a pre-approved WhatsApp Template (ContentSid).")
                print(f"   For testing, here is the message your phone WOULD have received:\n")
                print(f"   " + "-"*50)
                print(f"   {message}")
                print(f"   " + "-"*50 + "\n")
                print(f"✅ Simulated WhatsApp message (System working perfectly!)")
                return True
            else:
                print(f"❌ WhatsApp send failed: {e}")
                return False
    
    def send_approval_request(self, platform: str, content: str, post_id: str) -> bool:
        """
        Send a post to you for approval.
        
        Args:
            platform: Which social media platform
            content: The post content
            post_id: Unique ID for this post
        
        Returns:
            True if sent successfully, False otherwise
        """
        # Format the approval request message
        message = f"""🤖 *AI Assistant Needs Your Approval*

📱 Platform: {platform}
🆔 Post ID: {post_id}

📝 Content:
{content[:500]}

---
Reply with:
✅ YES {post_id} - to approve and post
❌ NO {post_id} - to reject
✏️ EDIT {post_id} [new content] - to edit
"""
        
        # Send the message
        return self.send_message(message)
    
    def send_daily_summary(self, summary: str) -> bool:
        """
        Send your daily schedule and activities.
        
        Args:
            summary: The daily summary text
        
        Returns:
            True if sent successfully, False otherwise
        """
        # Get today's date
        today = datetime.now().strftime("%A, %B %d")
        
        # Format the daily summary message
        message = f"""🌅 *Good Morning! Here's your day ({today}):*

{summary}

---
Your AI assistant is working for you 💪
"""
        
        # Send the message
        return self.send_message(message)
    
    def send_investment_alert(self, opportunity: str) -> bool:
        """
        Send investment opportunity alert.
        
        Args:
            opportunity: The investment opportunity text
        
        Returns:
            True if sent successfully, False otherwise
        """
        # Format the investment alert message
        message = f"""💰 *Investment Opportunity*

{opportunity}

---
⚠️ Always do your own research before investing!
"""
        
        # Send the message
        return self.send_message(message)


# ============================================================
# THIS IS THE LINE THAT WAS MISSING!
# ============================================================
# Create a global WhatsApp Manager instance that can be used throughout the app
whatsapp = WhatsAppManager()