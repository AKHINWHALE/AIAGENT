"""
tools.py - All the actions your AI agents can perform
Each tool is a function that does a specific task
"""

# Import necessary modules
import os
import json
import requests
from datetime import datetime
from crewai.tools import tool
from config import Config


# ============================================================
# TOOL 1: Search Trending Topics on the Internet
# ============================================================
@tool("Search Trending Topics")
def search_trending(niche: str) -> str:
    """
    Search the internet for trending topics in a specific niche.
    
    Args:
        niche: The topic to search for (e.g., "artificial intelligence", "business")
    
    Returns:
        A formatted string with trending topics and their sources
    
    Example:
        search_trending("artificial intelligence")
    """
    try:
        # The URL of the Tavily search API
        url = "https://api.tavily.com/search"
        
        # The data we're sending to the API
        payload = {
            "api_key": Config.TAVILY_KEY,  # Your Tavily API key
            "query": f"trending {niche} {datetime.now().strftime('%Y')}",  # What to search
            "search_depth": "advanced",  # How deep to search
            "max_results": 5  # Maximum number of results
        }
        
        # Send a POST request to the Tavily API
        response = requests.post(url, json=payload, timeout=30)
        
        # Convert the response to JSON (Python dictionary)
        data = response.json()
        
        # Create an empty list to store results
        results = []
        
        # Loop through the first 3 results
        for r in data.get("results", [])[:3]:
            # Format each result nicely
            result_text = f"• {r['title']}\n  {r['content'][:200]}...\n  Source: {r['url']}"
            results.append(result_text)
        
        # Return all results joined with double newlines
        # If no results, return a message
        return "\n\n".join(results) if results else "No trending topics found."
    
    except Exception as e:
        # If anything goes wrong, return an error message
        return f"Search failed: {str(e)}"


# ============================================================
# TOOL 2: Draft a Social Media Post
# ============================================================
@tool("Draft Social Media Post")
def draft_social_post(topic: str, platform: str, tone: str = "professional") -> str:
    """
    Create a draft social media post (NOT posted yet - needs approval).
    
    Args:
        topic: What the post is about
        platform: Which platform (twitter, instagram, linkedin, facebook)
        tone: The tone of the post (professional, casual, humorous)
    
    Returns:
        Confirmation that draft was created
    """
    # Create a dictionary with the post information
    draft = {
        "platform": platform,
        "topic": topic,
        "tone": tone,
        "content": f"[AI Generated Post about {topic} for {platform} in {tone} tone]",
        "created_at": datetime.now().isoformat(),
        "status": "pending_approval"
    }
    
    # Save the draft to a file
    with open("pending_posts.json", "a") as f:
        f.write(json.dumps(draft) + "\n")
    
    return f"DRAFT CREATED for {platform}. Send to WhatsApp for approval. Topic: {topic}"


# ============================================================
# TOOL 3: Read Recent Emails from Gmail
# ============================================================
@tool("Read Recent Emails")
def read_emails(count: int = 5) -> str:
    """
    Read the most recent emails from Gmail inbox.
    
    Args:
        count: Number of emails to read (default: 5)
    
    Returns:
        A formatted string with email subjects, senders, and previews
    """
    try:
        # Import email libraries
        import imaplib
        import email
        
        # Connect to Gmail's IMAP server (secure connection)
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        
        # Log in with your Gmail credentials
        mail.login(Config.GMAIL_USER, Config.GMAIL_PASSWORD)
        
        # Select the inbox
        mail.select("inbox")
        
        # Search for all emails
        status, messages = mail.search(None, "ALL")
        
        # Get the email IDs
        email_ids = messages[0].split()
        
        # Get the last N emails (most recent)
        recent = email_ids[-count:]
        
        # Create a list to store email summaries
        results = []
        
        # Loop through each recent email
        for e_id in recent:
            # Fetch the email data
            status, data = mail.fetch(e_id, "(RFC822)")
            
            # Parse the email
            msg = email.message_from_bytes(data[0][1])
            
            # Get the subject
            subject = msg.get("Subject", "No Subject")
            
            # Get the sender
            sender = msg.get("From", "Unknown")
            
            # Get the email body
            body = ""
            if msg.is_multipart():
                # If email has multiple parts (text + attachments)
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                # If email is just text
                body = msg.get_payload(decode=True).decode()
            
            # Format the email summary
            email_summary = f"From: {sender}\nSubject: {subject}\nPreview: {body[:150]}...\n"
            results.append(email_summary)
        
        # Log out from Gmail
        mail.logout()
        
        # Return all emails joined with separators
        return "\n---\n".join(results) if results else "No emails found."
    
    except Exception as e:
        # If anything goes wrong, return an error message
        return f"Email reading failed: {str(e)}. Check your Gmail App Password."


# ============================================================
# TOOL 4: Research Investment Opportunities
# ============================================================
@tool("Research Investments")
def research_investments(category: str = "stocks") -> str:
    """
    Research trending investment opportunities in stocks, crypto, or real estate.
    
    Args:
        category: Type of investment (stocks, crypto, real estate)
    
    Returns:
        A formatted string with investment opportunities
    """
    try:
        # The URL of the Tavily search API
        url = "https://api.tavily.com/search"
        
        # The data we're sending to the API
        payload = {
            "api_key": Config.TAVILY_KEY,
            "query": f"best {category} investments {datetime.now().strftime('%B %Y')} opportunities",
            "search_depth": "advanced",
            "max_results": 5
        }
        
        # Send the request
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        
        # Create a list to store results
        results = []
        
        # Loop through the first 3 results
        for r in data.get("results", [])[:3]:
            result_text = f"💰 {r['title']}\n{r['content'][:300]}...\nSource: {r['url']}"
            results.append(result_text)
        
        return "\n\n".join(results) if results else "No investment data found."
    
    except Exception as e:
        return f"Investment research failed: {str(e)}"


# ============================================================
# TOOL 5: Research PhD Thesis Topics
# ============================================================
@tool("Research Thesis Topics")
def research_thesis(field: str, keywords: str) -> str:
    """
    Search for recent academic papers and gaps in research for PhD thesis.
    
    Args:
        field: The academic field (e.g., "artificial intelligence", "machine learning")
        keywords: Specific keywords to search for
    
    Returns:
        A formatted string with research papers and gaps
    """
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": Config.TAVILY_KEY,
            "query": f"{field} {keywords} recent research papers 2024 2025 academic",
            "search_depth": "advanced",
            "max_results": 7
        }
        
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        
        results = []
        for r in data.get("results", [])[:5]:
            result_text = f"📚 {r['title']}\n{r['content'][:250]}...\nURL: {r['url']}"
            results.append(result_text)
        
        return "\n\n".join(results) if results else "No research found."
    
    except Exception as e:
        return f"Thesis research failed: {str(e)}"


# ============================================================
# TOOL 6: Suggest Skills to Learn
# ============================================================
@tool("Suggest AI Skills")
def suggest_skills(current_level: str = "beginner") -> str:
    """
    Suggest the next skills to learn to become an AI expert.
    
    Args:
        current_level: Your current level (beginner, intermediate, advanced)
    
    Returns:
        A formatted string with recommended skills
    """
    # Define skill paths for each level
    skill_paths = {
        "beginner": [
            "1. Python Programming (freeCodeCamp)",
            "2. Linear Algebra & Statistics (Khan Academy)",
            "3. Machine Learning Basics (Andrew Ng's course on Coursera)",
            "4. Pandas & NumPy for data handling"
        ],
        "intermediate": [
            "1. Deep Learning (Fast.ai course)",
            "2. NLP with Transformers (Hugging Face)",
            "3. MLOps & model deployment",
            "4. LLM fine-tuning and RAG systems"
        ],
        "advanced": [
            "1. Research paper implementation",
            "2. Distributed training",
            "3. AI agent frameworks (LangChain, CrewAI)",
            "4. Contributing to open-source AI projects"
        ]
    }
    
    # Get the skills for the specified level
    skills = skill_paths.get(current_level, skill_paths["beginner"])
    
    # Format and return the skills
    return f"🎯 Recommended skills for {current_level} level:\n\n" + "\n".join(skills)


# ============================================================
# TOOL 7: Get Today's Calendar/Schedule
# ============================================================
@tool("Get Today's Schedule")
def get_today_schedule() -> str:
    """
    Get today's calendar events and activities.
    NOTE: This is a placeholder. Connect to Google Calendar API for real data.
    
    Returns:
        A formatted string with today's schedule
    """
    # Get today's date
    today = datetime.now().strftime("%A, %B %d, %Y")
    
    # Return a placeholder schedule
    # In production, you'd connect to Google Calendar API here
    return f"""📅 Today's Schedule ({today}):

9:00 AM - Review WhatsApp approvals from AI agent
10:00 AM - Check investment research report
11:00 AM - PhD thesis research session
2:00 PM - Social media content review
4:00 PM - Email inbox zero
6:00 PM - Skill learning (30 min)

⚠️ Connect Google Calendar API for real events.
"""


# ============================================================
# TOOL 8: Save Post for WhatsApp Approval
# ============================================================
@tool("Save Post for Approval")
def save_for_approval(platform: str, content: str, image_url: str = "") -> str:
    """
    Save a social media post to be sent to WhatsApp for approval before posting.
    
    Args:
        platform: Which platform (twitter, instagram, linkedin, facebook)
        content: The post content
        image_url: Optional image URL
    
    Returns:
        Confirmation that post was saved
    """
    # Create a dictionary with the post information
    post = {
        "platform": platform,
        "content": content,
        "image_url": image_url,
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }
    
    # Save to the pending posts file
    with open("pending_posts.json", "a") as f:
        f.write(json.dumps(post) + "\n")
    
    return f"✅ Post saved for WhatsApp approval on {platform}"