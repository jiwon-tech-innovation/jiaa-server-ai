import asyncio
import sys
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

sys.path.append(".")

# Mock Config before importing modules that need it
with patch("app.core.config.get_settings") as mock_settings:
    # Setup Mock Settings values to prevent SQLAlchemy URL parsing error
    mock_settings.return_value.PROJECT_NAME = "Test"
    mock_settings.return_value.PG_USER = "user"
    mock_settings.return_value.PG_PASSWORD = "password"
    mock_settings.return_value.PG_HOST = "localhost"
    mock_settings.return_value.PG_PORT = "5432"
    mock_settings.return_value.PG_DB = "test_db"
    
    from app.services.statistic_service import statistic_service
    from app.services.predictor import predictor_service
    from app.api.v1.endpoints.prediction import predict_risk

class TestPredictionAPI(unittest.TestCase):
    
    def test_predict_risk_high_probability(self):
        """
        Scenario: User has 85% play ratio -> Should Warn = True
        """
        async def run_test():
            # Mock DB Session
            mock_db = AsyncMock()
            
            # Mock Statistic Service (Return 85.0%)
            with patch.object(statistic_service, 'get_play_ratio', new_callable=AsyncMock) as mock_stat:
                mock_stat.return_value = 85.0
                
                # Mock Predictor LLM (avoid real call)
                with patch.object(predictor_service, 'generate_prediction_warning', new_callable=AsyncMock) as mock_pred:
                    mock_pred.return_value = "데이터상 딴짓 각이네요?"
                    
                    # Call API Function directly
                    response = await predict_risk(
                        user_id="user123",
                        current_time="14:00",
                        db=mock_db
                    )
                    
                    # Verify
                    self.assertTrue(response.should_warn)
                    self.assertEqual(response.risk_percentage, 85.0)
                    self.assertEqual(response.message, "데이터상 딴짓 각이네요?")
                    
                    # Verify Calls
                    mock_stat.assert_awaited_once()
                    mock_pred.assert_awaited_once()

        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_test())
        loop.close()

    def test_predict_risk_low_probability(self):
        """
        Scenario: User has 20% play ratio -> Should Warn = False
        """
        async def run_test():
            mock_db = AsyncMock()
            
            with patch.object(statistic_service, 'get_play_ratio', new_callable=AsyncMock) as mock_stat:
                mock_stat.return_value = 20.0
                
                with patch.object(predictor_service, 'generate_prediction_warning', new_callable=AsyncMock) as mock_pred:
                    
                    response = await predict_risk(
                        user_id="user123",
                        current_time="14:00",
                        db=mock_db
                    )
                    
                    self.assertFalse(response.should_warn)
                    self.assertEqual(response.risk_percentage, 20.0)
                    self.assertIsNone(response.message)
                    
                    # Pred should NOT be called
                    mock_pred.assert_not_awaited()

        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_test())
        loop.close()

if __name__ == "__main__":
    unittest.main()
