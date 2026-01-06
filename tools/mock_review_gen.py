import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.memory_service import memory_service
from app.services.review_service import review_service
from datetime import datetime

async def run_test():
    print("🚀 [Test] Seeding Mock Data into Short-Term Memory...")
    
    # 1. Seed Mock Activities (Simulating Today's Events)
    # Note: timestamps are generated as 'now', so they will match 'today'.
    
    # Morning: Study (Dynamic Subject to prove AI)
    import random
    subjects = ["Quantum Physics", "Rust Language", "Kubernetes Internals", "Cooking Pasta"]
    subject = random.choice(subjects)
    memory_service.save_achievement(f"Studied {subject} for 2 hours.")
    print(f"DEBUG: Selected Subject: {subject}")
    await asyncio.sleep(0.1) # Ensure order
    
    # Late Morning: Slack off
    memory_service.save_violation("Caught playing League of Legends.", source="GameDetector")
    await asyncio.sleep(0.1)
    
    # Afternoon: Hard work but error
    memory_service._save_event(
        "User asked: 'How to fix ConnectionRefusedError in Python?'", 
        event_type="CHAT"
    )
    await asyncio.sleep(0.1)
    
    # Evening: Finish
    memory_service.save_achievement("Completed API implementation for Dev 5.")

    print("✅ [Test] Mock Data Seeded.")
    
    # 2. Trigger Blog Generation
    print("⏳ [Test] Generating Blog Post...")
    result = await review_service.generate_blog_post(
        error_log="ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it",
        solution_code="def fix_connection():\n    # Check if target port is open\n    # Ensure firewall allows connection\n    pass",
        user_id="dev1"
    )
    
    print("\n================ [GENERATED MARKDOWN] ================\n")
    # print(result.get("content"))
    with open("mock_blog_result.md", "w", encoding="utf-8") as f:
        f.write(result.get("content"))
    print("Saved to mock_blog_result.md")
    print("\n======================================================\n")

if __name__ == "__main__":
    asyncio.run(run_test())
