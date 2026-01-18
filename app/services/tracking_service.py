import grpc
import json
import re
from app.protos import tracking_pb2, tracking_pb2_grpc
from app.core.crypto import decrypt_data_raw
from app.services.memory_service import memory_service
from app.core.llm import get_llm, HAIKU_MODEL_ID
from app.services import stt, chat
from app.schemas.intelligence import ChatRequest


from app.protos import core_pb2, core_pb2_grpc

class TrackingService(tracking_pb2_grpc.TrackingServiceServicer, core_pb2_grpc.CoreServiceServicer):
    
    # ... (TranscribeAudio remains same) ...

    async def TranscribeAudio(self, request_iterator, context):
        """
        Receives AudioStream from Client (via TrackingService), aggregates bytes, performs STT -> Chat.
        """
        audio_buffer = bytearray()
        final_media_info = {}

        try:
            async for request in request_iterator:
                audio_buffer.extend(request.audio_data)
                
                # Validate media_info_json
                if hasattr(request, 'media_info_json') and request.media_info_json:
                    try:
                        info = json.loads(request.media_info_json)
                        final_media_info.update(info)
                    except:
                        pass

                if request.is_final:
                    break
        except Exception as e:
            print(f"gRPC Stream Error: {e}")

        # 1. STT
        stt_response = await stt.transcribe_bytes(bytes(audio_buffer), file_ext="mp3")
        user_text = stt_response.text
        print(f"🗣️ [Tracking] User said: \"{user_text}\"")

        if not user_text or not user_text.strip():
            # Check which AudioResponse to return (Tracking vs Core)
            # We default to Tracking's because this method is bound to TrackingService mostly
            return tracking_pb2.AudioResponse(
                transcript="(No speech detected)",
                is_emergency=False,
                intent="{}"
            )

        # 2. Chat
        user_id = final_media_info.get("user_id", "dev1")
        chat_request = ChatRequest(text=user_text, user_id=user_id)
        chat_response = await chat.chat_with_persona(chat_request)

        # 3. Construct Intent
        intent_data = {
            "text": chat_response.message,
            "state": chat_response.judgment,
            "type": chat_response.intent,
            "command": chat_response.action_code,
            "parameter": chat_response.action_detail or "",
            "emotion": chat_response.emotion or "NORMAL"
        }
        
        final_intent = json.dumps(intent_data, ensure_ascii=False)

        # Return Tracking Response (Standard)
        return tracking_pb2.AudioResponse(
            transcript=user_text,
            is_emergency=False,
            intent=final_intent
        )

    async def SyncClient(self, request_iterator, context):
        """
        Bidirectional Stream for Client Heartbeat (CoreService).
        Handles Game Detection & Nagging.
        """
        print(f"⚡ [Core] SyncClient Connected")
        
        SERVER_BLACKLIST = ["Overwatch", "MapleStory", "Destiny", "Battle.net", "Steam", "League of Legends", "Riot Client"]
        
        try:
            async for heartbeat in request_iterator:
                # 1. Parse Apps
                apps = []
                if heartbeat.apps_json:
                    try:
                        apps = json.loads(heartbeat.apps_json)
                    except:
                        pass
                
                # Skip detection if app list is empty
                if not apps:
                    continue

                kill_target = ""
                command_type = core_pb2.ServerCommand.NONE
                payload = ""

                # 2. Hybrid Game Detection
                
                # 2-1. Fast Blacklist
                for app in apps:
                    for bad in SERVER_BLACKLIST:
                        if bad.lower() in app.lower():
                            kill_target = app
                            command_type = core_pb2.ServerCommand.KILL_PROCESS
                            payload = app
                            print(f"🚫 [Core] BLACKLIST DETECTED: {app}")
                            break
                    if command_type != core_pb2.ServerCommand.NONE:
                        break
                
                # 2-2. AI Detection (If no blacklist hit)
                if command_type == core_pb2.ServerCommand.NONE:
                    try:
                        # Throttle AI checks? (Maybe doing it every heartbeat is too much?)
                        # But heartbeat is 1s. Let's rely on GameDetector being fast or create a cache if needed.
                        # For now, let's call it.
                        from app.services import game_detector
                        from app.schemas.game import GameDetectRequest
                        
                        detect_req = GameDetectRequest(apps=apps)
                        ai_result = await game_detector.detect_games(detect_req)
                        
                        if ai_result.is_game_detected:
                            kill_target = ai_result.target_app
                            command_type = core_pb2.ServerCommand.KILL_PROCESS
                            payload = kill_target
                            msg = ai_result.message
                            
                            # Also send a MESSAGE to scold user?
                            # Current protocol only supports one command per heartbeat response? 
                            # Or we can yield multiple.
                            
                            print(f"🤖 [Core] AI DETECTED GAME: {kill_target}")
                            
                            # Yield Message First
                            if msg:
                                yield core_pb2.ServerCommand(
                                    type=core_pb2.ServerCommand.SHOW_MESSAGE,
                                    payload=msg
                                )
                    except Exception as e:
                        print(f"⚠️ [Core] AI Error: {e}")

                # 3. Yield Command
                if command_type != core_pb2.ServerCommand.NONE:
                    yield core_pb2.ServerCommand(
                        type=command_type,
                        payload=payload
                    )
        
        except Exception as e:
            print(f"❌ [Core] SyncClient Disconnected: {e}")

    async def SendAppList(self, request, context):
        # ... (Legacy Implementation or just redirect) ...
        return tracking_pb2.AppListResponse(success=True, message="Deprecated. Use SyncClient.")

    async def ReportAnalysisResult(self, request, context):
        print(f"📊 [Core] Analysis Report: {request.type}")
        return core_pb2.Ack(success=True)
