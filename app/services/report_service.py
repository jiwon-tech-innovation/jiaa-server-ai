from datetime import datetime
from app.services.calendar_service import calendar_service
from app.services.statistic_service import statistic_service
from app.services.memory_service import memory_service
from app.core.llm import get_llm, SONNET_MODEL_ID
from langchain_core.prompts import PromptTemplate

class ReportService:
    def __init__(self):
        # [User Request] Use Sonnet for higher quality reports and better Korean support
        self.llm = get_llm(model_id=SONNET_MODEL_ID, temperature=0.7)

    async def generate_daily_wrapped(self, user_id: str) -> str:
        """
        Generates a "Daily Wrapped" report by triangulating Plan vs Actual vs Said.
        """
        # 1. Fetch Plans (Calendar)
        plans = calendar_service.get_todays_plan()
        plan_str = "\n".join([f"- [{p['start']}~{p['end']}] {p['summary']}" for p in plans])
        if not plan_str: plan_str = "(No plans recorded)"

        # 2. Fetch Actuals (InfluxDB Timeline)
        timeline = await statistic_service.get_daily_timeline(user_id)
        actual_str = "\n".join(timeline)
        if not actual_str: actual_str = "(No significant activity logs)"

        # 3. Fetch Said (Vector Memory - Daily Summary)
        # We reuse get_daily_activities from MemoryService, but it searches STM.
        said_list = memory_service.get_daily_activities()
        said_str = "\n".join(said_list)

        # 4. Fetch Quiz Results (Performance) - Now from DB via quiz_service
        from app.services.quiz_service import quiz_service
        quiz_list = await quiz_service.get_daily_quiz_results(user_id)
        # Fallback to memory_service if DB returns empty
        if not quiz_list:
            quiz_list = memory_service.get_daily_quiz_results()
        quiz_str = "\n".join(quiz_list)
        if not quiz_str: quiz_str = "(No quizzes taken)"

        # 5. LLM Generation
        prompt = f"""
You are "Alpine", the critical code reviewer and life coach.
Write a "Daily Wrapped" (Daily Retrospective) for the user "Dev 1".

### DATA SOURCES
1. [PLAN] What they planned (Google Calendar):
{plan_str}

2. [ACTUAL] What they did (System Logs):
{actual_str}

3. [SAID] What they claimed/chatted (Chat Logs):
{said_str}

4. [PERFORMANCE] Quiz Scores:
{quiz_str}

### INSTRUCTIONS
- **Triangulation Analysis**: Compare [PLAN] vs [ACTUAL] vs [PERFORMANCE].
- **Fact Check**:
  - Did they plan to study but play games? ([PLAN] vs [ACTUAL])
  - Did they claim to study hard but fail the quiz? ([SAID] vs [PERFORMANCE]) -> " 입만 살았군요."
- Tone: Sharp, Analytical, Witty, slightly "Tsundere" but heavy on FACTS.
- Format: Markdown.

### OUTPUT STRUCTURE
# 📅 Daily Report ({datetime.now().strftime("%Y-%m-%d")})

## 📊 Summary Grade
- **Grade**: (A/B/C/F)
- **Trust Score Change**: (From Memory Service trust update)

## 🔍 Plan vs Reality
| Included | Actual | Verdict |
|----------|--------|---------|
| (Plan Item) | (Actual Log) | (Pass/Fail) |

## 📉 Performance Review
- (Comment on Quiz Scores vs Activity)

## 🤥 The Lie Detector
- (Did [SAID] match [ACTUAL]?)

## 🚀 Action Item for Tomorrow
- (Specific advice)

**IMPORTANT: Write the ENTIRE report in Korean (한국어). Do not use English for headings.**
"""
        response = await self.llm.ainvoke(prompt)
        return response.content

report_service = ReportService()
