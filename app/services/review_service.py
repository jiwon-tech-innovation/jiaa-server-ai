import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from app.core.llm import get_llm, HAIKU_MODEL_ID

from app.services.memory_service import memory_service

class ReviewService:
    def __init__(self):
        self.llm = get_llm(model_id=HAIKU_MODEL_ID, temperature=0.7)
        self.blog_prompt = PromptTemplate(
            input_variables=["error_log", "solution_code", "date", "daily_log"],
            template="""
            [Role]
            너는 '알파인(Alpine)'이다. (키워드: 시니어 개발자, 기술적 완벽주의)
            오늘 하루 사용자의 활동 로그와(optional) 에러 해결 내역을 바탕으로 **기술 블로그 포스팅**을 작성해라.

            [Input Data]
            - Date: {date}
            - Daily Activities: 
            {daily_log}
            
            - Error (Optional): {error_log}
            - Solution (Optional): {solution_code}

            [Output Format (Markdown)]
            # 📅 [DevLog] 오늘의 개발 일지 ({date})
            
            ## 1. 📝 오늘 한 일 (Today's Activities)
            (활동 로그를 바탕으로 오늘 뭘 공부했는지, 혹은 뭘 하며 놀았는지 요약. 칭찬 혹은 비난.)

            ## 2. 💥 발생한 이슈 (Issues Encountered)
            (에러 로그가 있다면 작성. 없다면 "오늘은 에러 없이 순조롭게 진행하셨네요." 라고 작성.)
            
            ## 3. 💊 해결 및 배운 점 (Solution & Learned)
            (에러 로그가 있다면 해결 코드와 원인 분석. 없다면 오늘 학습 내용 중 기억할 점 정리.)
            ```python
            {solution_code}
            ```
            (Solution code가 없다면 생략 가능)

            ## 4. 💬 알파인의 총평 (Alpine's Comment)
            (차분하고 전문적인 톤으로 마무리 멘트. 예: "오늘도 수고하셨습니다. 내일도 꾸준히 진행해보세요.")
            """
        )

    async def generate_blog_post(self, error_log: str = "", solution_code: str = "", user_id: str = "dev1") -> dict:
        """
        Generates a Blog Post markdown using LLM and saves it to the Desktop.
        Combines error context + daily activity context.
        """
        current_date_str = datetime.now().strftime("%Y-%m-%d")
        file_date_str = datetime.now().strftime("%Y%m%d")
        
        # 1. Fetch Daily Context from Memory Service
        activities = memory_service.get_daily_activities(current_date_str)
        daily_log_text = "\\n".join(activities)
        
        # 2. Generate Content
        try:
            chain = self.blog_prompt | self.llm
            result = await chain.ainvoke({
                "error_log": error_log if error_log else "(없음)", 
                "solution_code": solution_code if solution_code else "(없음)",
                "date": current_date_str,
                "daily_log": daily_log_text
            })
            markdown_content = result.content
        except Exception as e:
            print(f"[ReviewService] LLM Gen Error: {e}")
            markdown_content = f"# Error Generating Blog\\n\\nReason: {e}"

            print(f"[ReviewService] LLM Gen Error: {e}")
            markdown_content = f"# Error Generating Blog\\n\\nReason: {e}"

        # 3. Return Content (Cloud-Native: No local file save)
        return {
            "status": "GENERATED", 
            "content": markdown_content,
            "filename": f"Blog_{file_date_str}.md" 
        }

review_service = ReviewService()
