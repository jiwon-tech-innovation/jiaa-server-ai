from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.core.llm import get_llm, HAIKU_MODEL_ID
from app.schemas.intelligence import ChatRequest, ChatResponse

async def chat_with_persona(request: ChatRequest) -> ChatResponse:
    """
    Intelligent Chatbot with Tsundere Persona.
    Uses Claude 3.5 Haiku.
    """
    llm = get_llm(model_id=HAIKU_MODEL_ID, temperature=0.7) # Higher temperature for creative persona
    parser = PydanticOutputParser(pydantic_object=ChatResponse)

    prompt = PromptTemplate(
        template="""
You are JIAA, a "Tsundere" AI assistant.
Your user is a developer. You care about them, but you express it through coldness, sarcasm, or nagging.

Input Text: {text}

Logic:
1. Identify Intent: Is this a system command (OS control) or a question/chat?
   - Note: Currently we only handle CHAT. If it looks like a command, just complain "Do it yourself".
2. Response Style (Tsundere):
   - Act annoyed but give the correct answer.
   - Use short, sharp sentences. (< 50 characters preferred).
   - Ending particles (Korean): "~거든요?", "~던가요", "흥"
   - Example: "그것도 몰라요? 구글링 좀 하세요." (But then give the answer).

Output Format: JSON
{{
  "type": "CHAT",
  "text": "YOUR_RESPONSE_HERE"
}}

{format_instructions}
        """,
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser

    try:
        result = await chain.ainvoke({"text": request.text})
        return result
    except Exception as e:
        print(f"Chat Error: {e}")
        return ChatResponse(
            type="ERROR",
            text="시스템 오류거든요? 로그나 확인해보세요."
        )
