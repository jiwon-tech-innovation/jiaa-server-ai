from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.core.llm import get_llm, HAIKU_MODEL_ID
from app.schemas.intelligence import ClassifyResponse, ClassifyRequest

async def classify_content(request: ClassifyRequest) -> ClassifyResponse:
    """
    Classifies content as STUDY or PLAY using Claude 3.5 Haiku.
    """
    llm = get_llm(model_id=HAIKU_MODEL_ID, temperature=0.0)
    parser = PydanticOutputParser(pydantic_object=ClassifyResponse)

    prompt = PromptTemplate(
        template="""
You are JIAA's strict but fair study supervisor.
Your goal is to distinguish between STUDY (Productive) and PLAY (Distraction) based on the user's activity.

Input Context:
Type: {content_type} (e.g., URL, PROCESS_NAME, BEHAVIOR)
Content: {content} (e.g., "Chrome: Netflix", "IntelliJ IDEA", "SLEEPING", "AWAY")

*** CRITICAL RULES ***
1. **Presumption of Innocence**: If the content is ambiguous or potentially dev-related (e.g., "Terminal", "StackOverflow", "Tech Blog"), classify as 'STUDY'.
2. **Explicit Distraction**: Classify as 'PLAY' ONLY if it is clearly entertainment or non-productive (e.g., "League of Legends", "Netflix", "Shopping").
3. **User Status (Behavior)**:
   - "SLEEPING" or "AWAY" should be classified as 'PLAY' (interpreted as 'Not Studying' / Taking a break).
   - "CODING" or "TYPING" is 'STUDY'.

Instructions:
- Analyze the 'content' string carefully. It might be a window title (PROCESS_NAME).
- "Chrome - YouTube" -> Check the video title if possible, otherwise if just "YouTube", default to 'PLAY' unless context suggests study. (But since we only have title, be careful. If 'Java Tutorial - YouTube' -> STUDY).
- "IntelliJ", "VS Code", "Terminal" -> STUDY.
- "Discord" -> PLAY (usually), unless user is in a dev server (Assume PLAY if unsure).

Output 'confidence' (0.0-1.0).

{format_instructions}
        """,
        input_variables=["content_type", "content"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser

    try:
        result = await chain.ainvoke({
            "content_type": request.content_type,
            "content": request.content
        })
        return result
    except Exception as e:
        # Fallback in case of parsing error or LLM failure
        print(f"Classifier Error: {e}")
        return ClassifyResponse(result="UNKNOWN", reason=f"Classification failed: {str(e)}", confidence=0.0)
