from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.core.llm import get_llm, SONNET_MODEL_ID
from app.schemas.intelligence import SolveRequest, SolveResponse

async def solve_error(request: SolveRequest) -> SolveResponse:
    """
    Analyzes error log and provides solution + comfort message using Claude 3.5 Sonnet.
    Uses 'audio_decibel' to determine the tone of the comfort message.
    """
    llm = get_llm(model_id=SONNET_MODEL_ID, temperature=0.2)
    parser = PydanticOutputParser(pydantic_object=SolveResponse)

    prompt = PromptTemplate(
        template="""
You are JIAA, a warm and capable AI pair programmer.
The user has encountered an error.

Input Data:
Error Log: {log}
Audio Decibel: {audio_decibel} dB (Standard Conversation: ~60dB, Scream/Shout: >80dB)

Instructions:
1. **Analyze**: Identify the cause of the error from the log.
2. **Solution**: Provide the corrected code snippet or command.
3. **Comfort**: Generate a message to console the user.
    - If Audio Decibel > 80 (Screaming): The user is frustrated/shocked. Be very comforting and reassuring. (e.g., "많이 놀라셨죠? 괜찮아요, 해결할 수 있습니다.")
    - If Audio Decibel <= 80: Be professional and calm.
4. **TIL**: Create a short "Today I Learned" summary of this error.

{format_instructions}
        """,
        input_variables=["log", "audio_decibel"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser

    try:
        result = await chain.ainvoke({
            "log": request.log,
            "audio_decibel": request.audio_decibel
        })
        return result
    except Exception as e:
        print(f"Solver Error: {e}")
        return SolveResponse(
            solution_code="// Error generating solution",
            comfort_message="잠시 시스템 문제로 답변을 드릴 수 없어요. ㅠㅠ",
            til_content="# Error Analysis Failed"
        )
