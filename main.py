"""
main.py - The Main Entry Point for Your AI Assistant
Run this file to start your AI working for you!
"""
import sys
import os
from crewai import Crew, Task
from agents import get_all_agents
from whatsapp import whatsapp
from approval import approval_manager
from scheduler import start_scheduler

def run_manual_task(task_description: str):
    """Run a specific task manually"""
    print(f"\n🎯 Running task: {task_description}\n")
    
    # Get all 10 agents
    agents = get_all_agents()
    
    # Smart routing: pick the right agent based on your request
    if "email" in task_description.lower():
        agent = agents["email"]
    elif "social" in task_description.lower() or "post" in task_description.lower():
        agent = agents["social_media"]
    elif "linkedin" in task_description.lower():
        agent = agents["linkedin"]
    elif "invest" in task_description.lower():
        agent = agents["investment"]
    elif "thesis" in task_description.lower() or "phd" in task_description.lower():
        agent = agents["phd_researcher"]
    elif "skill" in task_description.lower() or "learn" in task_description.lower():
        agent = agents["skill_advisor"]
    elif "trend" in task_description.lower():
        agent = agents["trend_scout"]
    elif "calendar" in task_description.lower() or "schedule" in task_description.lower():
        agent = agents["calendar"]
    else:
        agent = agents["business"]
    
    # Create a Crew with the chosen agent
    crew = Crew(
        agents=[agent],
        tasks=[
            Task(
                description=task_description,
                expected_output="A detailed, actionable response",
                agent=agent  # <--- THIS IS THE NEW REQUIRED LINE
            )
        ]
    )
    
    # Run the crew and get the result
    result = crew.kickoff()
    
    print("\n" + "="*60)
    print("RESULT:")
    print("="*60)
    print(result)
    return result

def interactive_menu():
    """Interactive menu for manual control"""
    while True:
        print("\n" + "="*60)
        print("🤖 YOUR PERSONAL AI ASSISTANT - MAIN MENU")
        print("="*60)
        print("1. 🚀 Start autonomous mode (works while you sleep)")
        print("2. 📱 Send test WhatsApp message")
        print("3. 📧 Check emails now")
        print("4. 🔍 Scout trends now")
        print("5. 💰 Research investments now")
        print("6. 📚 PhD research now")
        print("7. 🎓 Get skill suggestions")
        print("8. 📅 Get today's schedule")
        print("9. ✅ Check pending approvals")
        print("10. 🎯 Run custom task")
        print("0. 👋 Exit")
        print("="*60)
        
        choice = input("\nEnter choice (0-10): ").strip()
        
        if choice == "1":
            start_scheduler()
        elif choice == "2":
            whatsapp.send_message("🧪 Test message from your AI assistant! If you see this on WhatsApp, it works! ✅")
        elif choice == "3":
            run_manual_task("Check my recent emails and summarize the important ones")
        elif choice == "4":
            run_manual_task("Search for trending topics in AI and business, draft 2 social posts and save for approval")
        elif choice == "5":
            run_manual_task("Research current investment opportunities in stocks and crypto")
        elif choice == "6":
            run_manual_task("Find recent research papers and gaps for my PhD thesis in AI")
        elif choice == "7":
            run_manual_task("Suggest skills I should learn to become an AI expert")
        elif choice == "8":
            run_manual_task("Get today's schedule and activities")
        elif choice == "9":
            posts = approval_manager.get_pending_posts()
            print(f"\n📋 {len(posts)} posts pending approval")
            for p in posts:
                print(f"  • {p.get('platform')}: {p.get('content', '')[:80]}...")
        elif choice == "10":
            task = input("\nEnter your custom task: ").strip()
            if task:
                run_manual_task(task)
        elif choice == "0":
            print("\n👋 Goodbye! Your AI assistant is shutting down.")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 0 and 10.")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🤖 PERSONAL AI ASSISTANT INITIALIZING...")
    print("="*60)
    
    # Check if API keys are loaded
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API Key loaded successfully.")
    else:
        print("⚠️ WARNING: OPENAI_API_KEY not found in .env file!")
        
    print("✅ 10 AI Agents are initialized and ready to work for you!")
    print("="*60)
    
    # If you typed a command after 'python main.py', run it
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        run_manual_task(task)
    else:
        # Otherwise, show the interactive menu
        interactive_menu()


if __name__ == "__main__":
    main()