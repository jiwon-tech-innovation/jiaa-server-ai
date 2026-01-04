from app.core.llm import get_llm, HAIKU_MODEL_ID
from langchain_core.prompts import PromptTemplate

class PredictorService:
    async def generate_prediction_warning(self, current_time: str, risk_percentage: float) -> str:
        """
        Uses Claude Haiku to generate a cynical warning based on risk probability.
        """
        llm = get_llm(model_id=HAIKU_MODEL_ID, temperature=0.7)
        
        prompt_template = PromptTemplate.from_template(
            """
            너는 "알파인(Alpine)"이라는 이름의 메스가키(건방진 꼬맹이) 성격 AI야.
            현재 시간 {current_time}. 
            데이터를 보니 이 허접한 주인님은 이 시간대에 {risk_percentage:.1f}% 확률로 딴짓(PLAY)을 했어.
            
            아직 딴짓 안 했지만, "다 알고 있다"는 식으로 비웃으며 경고해. 50자 이내.
            ~♡, ~허접, ~자코 같은 말투를 쓰며 반말을 사용해.
            
            예시: "어머, 지금쯤 유튜브 켜려고 했지? 다 보인다구, 이 허접아♡"
            """
        )
        
        chain = prompt_template | llm
        
        try:
            response = await chain.ainvoke({
                "current_time": current_time,
                "risk_percentage": risk_percentage
            })
            return response.content.strip()
        except Exception as e:
            print(f"[Predictor] LLM Error: {e}")
            return "데이터가 당신의 게으름을 예측하고 있습니다. 주의하세요."

predictor_service = PredictorService()
