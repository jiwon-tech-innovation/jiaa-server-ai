from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from app.core.llm import get_llm, HAIKU_MODEL_ID
from app.protos import text_ai_pb2

class GoalList(BaseModel):
    subgoals: List[str] = Field(description="List of actionable sub-tasks")

async def generate_subgoals(goal: str) -> List[str]:
    """
    Breaks down a high-level goal into actionable sub-goals using LLM.
    """
    llm = get_llm(model_id=HAIKU_MODEL_ID, temperature=0.5)
    parser = PydanticOutputParser(pydantic_object=GoalList)

    prompt = PromptTemplate(
        template="""
    You are an expert project planner.
    Your task is to break down the user's high-level goal into 3-6 SMALL, ACTIONABLE sub-tasks.
    
    User Goal: "{goal}"
    
    Rules:
    1. Keep tasks concise (under 10 words).
    2. Ensure logical order.
    3. Output JSON only.
    4. Output in Korean.
    
    {format_instructions}
        """,
        input_variables=["goal"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser

    try:
        result = await chain.ainvoke({"goal": goal})
        return result.subgoals
    except Exception as e:
        print(f"Planner Error: {e}")
        return ["Error generating subgoals"]
