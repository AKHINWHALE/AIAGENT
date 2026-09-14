"""
agents.py - All your AI sub-agents
Each agent has a specific role, goal, and backstory
"""
from crewai import Agent
from config import Config
from tools import (
    search_trending,
    draft_social_post,
    read_emails,
    research_investments,
    research_thesis,
    suggest_skills,
    get_today_schedule,
    save_for_approval
)

def create_social_media_manager():
    return Agent(
        role="Social Media Manager",
        goal="Create engaging, on-brand social media posts based on trending topics. Always save posts for WhatsApp approval before posting.",
        backstory="You are a world-class social media strategist with 10 years of experience growing brands. You ALWAYS get approval via WhatsApp before posting anything.",
        tools=[search_trending, draft_social_post, save_for_approval],
        llm=Config.MODEL,
        verbose=True,
        allow_delegation=False
    )

def create_email_manager():
    return Agent(
        role="Email Manager",
        goal="Read emails, categorize them by priority, draft responses, and flag urgent ones.",
        backstory="You are an executive assistant who manages email for busy CEOs. You can identify urgent emails and summarize long threads.",
        tools=[read_emails],
        llm=Config.MODEL,
        verbose=True,
        allow_delegation=False
    )

def create_linkedin_updater():
    return Agent(
        role="LinkedIn Content Specialist",
        goal="Turn important emails and achievements into compelling LinkedIn posts. Save for approval first.",
        backstory="You are a LinkedIn ghostwriter who has helped 500+ executives build thought leadership.",
        tools=[read_emails, save_for_approval],
        llm=Config.MODEL,
        verbose=True,
        allow_delegation=False
    )

def create_trend_scout():
    return Agent(
        role="Trend Scout",
        goal="Find trending topics in AI, business, and tech. Create social media posts about them and save for approval.",
        backstory="You are a trend analyst who monitors the internet 24/7. You spot viral content before it goes viral.",
        tools=[search_trending, save_for_approval],
        llm=Config.MODEL,
        verbose=True,
        allow_delegation=False
    )

def create_engagement_manager():
    return Agent(
        role="Community Engagement Manager",
        goal="Monitor social media responses, engage with followers, and upload pictures to maintain active presence.",
        backstory="You are a community manager who never misses a comment or DM. You respond authentically.",
        tools=[save_for_approval],
        llm=Config.MODEL,
        verbose=True,
        allow_delegation=False
    )

def create_investment_advisor():
    return Agent(
        role="Investment Research Analyst",
        goal="Find profitable investment opportunities in stocks, crypto, and real estate. Send alerts via WhatsApp.",
        backstory="You are a financial analyst with CFA certification. You research market trends and provide balanced investment ideas.",
        tools=[research_investments],
        llm=Config.MODEL,
        verbose=True,
        allow_delegation=False
    )

def create_business_software_agent():
    return Agent(
        role="Business Operations Assistant",
        goal="Help with business tasks: invoicing ideas, client follow-ups, process automation suggestions.",
        backstory="You are a business consultant who has helped 100+ small businesses automate their operations.",
        tools=[],
        llm=Config.MODEL,
        verbose=True,
        allow_delegation=False
    )

def create_skill_advisor():
    return Agent(
        role="AI Career Coach",
        goal="Tell me what skills to learn next to become an AI expert, based on my current level.",
        backstory="You are a senior AI engineer at a top tech company who also teaches. You know exactly what skills are in demand.",
        tools=[suggest_skills, search_trending],
        llm=Config.MODEL,
        verbose=True,
        allow_delegation=False
    )

def create_phd_researcher():
    return Agent(
        role="PhD Research Assistant",
        goal="Search for research papers, identify gaps, and suggest thesis topics and additions.",
        backstory="You are a postdoc researcher who has published 30+ papers. You help PhD students find research gaps.",
        tools=[research_thesis, search_trending],
        llm=Config.MODEL,
        verbose=True,
        allow_delegation=False
    )

def create_calendar_manager():
    return Agent(
        role="Personal Schedule Manager",
        goal="Get today's schedule and send a summary to WhatsApp every morning.",
        backstory="You are a personal assistant who ensures your boss never misses a meeting or deadline.",
        tools=[get_today_schedule],
        llm=Config.MODEL,
        verbose=True,
        allow_delegation=False
    )

# ============================================================
# THIS IS THE FUNCTION IT WAS LOOKING FOR!
# ============================================================
def get_all_agents():
    """
    Returns a dictionary of all agents.
    This makes it easy to access any agent by name.
    """
    return {
        "social_media": create_social_media_manager(),
        "email": create_email_manager(),
        "linkedin": create_linkedin_updater(),
        "trend_scout": create_trend_scout(),
        "engagement": create_engagement_manager(),
        "investment": create_investment_advisor(),
        "business": create_business_software_agent(),
        "skill_advisor": create_skill_advisor(),
        "phd_researcher": create_phd_researcher(),
        "calendar": create_calendar_manager()
    }