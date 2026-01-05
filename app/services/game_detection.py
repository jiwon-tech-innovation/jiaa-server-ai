"""
Game Detection Service
AI 기반으로 실행 중인 앱 목록에서 게임을 감지하는 서비스
"""

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.llm import get_llm, HAIKU_MODEL_ID
from app.schemas.intelligence import GameDetectionRequest, GameDetectionResponse
from typing import List


# 알려진 게임 목록 (빠른 감지용)
KNOWN_GAMES = [
    "League of Legends", "LeagueClient", "Riot Client",
    "Minecraft", "Steam", "Epic Games",
    "Valorant", "PUBG", "Overwatch",
    "Genshin Impact", "원신",
    "MapleStory", "메이플스토리",
    "Lost Ark", "로스트아크",
    "Diablo", "StarCraft", "스타크래프트",
    "FIFA", "Fortnite", "포트나이트",
    "Roblox", "Among Us",
    "Apex Legends", "Call of Duty",
    "World of Warcraft", "WoW",
    "Dota 2", "Counter-Strike", "CS2",
    "Hearthstone", "하스스톤",
    "BlueStacks",  # 모바일 게임 에뮬레이터
]


def quick_detect_games(apps: List[str]) -> List[str]:
    """빠른 게임 감지 (알려진 게임 목록 기반)"""
    detected = []
    for app in apps:
        app_lower = app.lower()
        for game in KNOWN_GAMES:
            if game.lower() in app_lower:
                detected.append(app)
                break
    return detected


async def detect_games_with_ai(request: GameDetectionRequest) -> GameDetectionResponse:
    """
    AI 기반 게임 감지
    1. 먼저 알려진 게임 목록으로 빠른 감지
    2. 확실하지 않으면 Claude Haiku로 분류
    """
    apps = request.apps
    
    # 1. 빠른 감지 (알려진 게임)
    quick_detected = quick_detect_games(apps)
    
    if quick_detected:
        # 바로 감지됨 - AI 호출 없이 반환
        return GameDetectionResponse(
            detected_games=quick_detected,
            is_game_detected=True,
            command="KILL",
            target_app=quick_detected[0],  # 첫 번째 게임 종료
            message=f"🎮 {quick_detected[0]} 감지됨! 공부 시간에 게임은 안 돼!"
        )
    
    # 2. AI 기반 분류 (알려진 게임이 없을 때)
    if len(apps) == 0:
        return GameDetectionResponse(
            detected_games=[],
            is_game_detected=False
        )
    
    try:
        llm = get_llm(model_id=HAIKU_MODEL_ID, temperature=0.0)
        
        prompt = PromptTemplate(
            template="""You are a strict study supervisor. Analyze the list of running applications and identify any games or gaming-related applications.

Running Applications:
{apps}

Respond in JSON format:
{{
    "detected_games": ["List of game application names found"],
    "is_game_detected": true/false,
    "reason": "Brief explanation"
}}

Rules:
- Games include: video games, mobile game emulators, gaming launchers (Steam, Epic Games, Riot Client, etc.)
- NOT games: browsers, IDEs, productivity apps, music players, communication apps (unless clearly gaming-related)
- Be conservative: if unsure, do NOT mark as game

IMPORTANT: Output ONLY the JSON object. No explanations.
""",
            input_variables=["apps"]
        )
        
        chain = prompt | llm
        result = await chain.ainvoke({"apps": ", ".join(apps)})
        
        # Parse LLM response
        import json
        content = result.content if hasattr(result, 'content') else str(result)
        
        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        parsed = json.loads(content.strip())
        detected = parsed.get("detected_games", [])
        is_detected = parsed.get("is_game_detected", False)
        
        if is_detected and detected:
            return GameDetectionResponse(
                detected_games=detected,
                is_game_detected=True,
                command="KILL",
                target_app=detected[0],
                message=f"🎮 AI가 {detected[0]}을(를) 게임으로 감지했어! 공부해!"
            )
        else:
            return GameDetectionResponse(
                detected_games=[],
                is_game_detected=False
            )
            
    except Exception as e:
        print(f"Game Detection AI Error: {e}")
        # AI 실패 시 빈 응답 (게임 없음으로 처리)
        return GameDetectionResponse(
            detected_games=[],
            is_game_detected=False,
            message=f"AI 분석 실패: {str(e)}"
        )
