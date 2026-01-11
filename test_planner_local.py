import asyncio
from app.services import planner

async def test_planner():
    goal = "Create a React-based TODO app with Firebase backend"
    print(f"🎯 Testing Goal: {goal}")
    
    subgoals = await planner.generate_subgoals(goal)
    
    print("\n✅ Generated Subgoals:")
    for i, sg in enumerate(subgoals, 1):
        print(f"{i}. {sg}")

if __name__ == "__main__":
    asyncio.run(test_planner())
