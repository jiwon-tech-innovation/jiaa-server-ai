import grpc
import logging
from concurrent import futures
from app.protos import audio_pb2, audio_pb2_grpc
from app.services import stt, chat
from app.schemas.intelligence import ChatRequest

# Configure Service
class SpeechService(audio_pb2_grpc.SpeechServiceServicer):
    async def SendAudioStream(self, request_iterator, context):
        """
        Receives AudioStream, aggregates bytes, performs STT -> Chat.
        """
        audio_buffer = bytearray()
        
        # NOTE: gRPC async iterator usage depends on the server type (AsyncIO)
        # Assuming we run this in an asyncio compatible gRPC server
        try:
            async for request in request_iterator:
                audio_buffer.extend(request.audio_data)
                
                if request.is_final:
                    break
        except Exception as e:
            print(f"gRPC Stream Error: {e}")
            # If standard iterator (sync)
            # for request in request_iterator: ...

        # 1. STT (Convert gathered bytes)
        # Assume valid audio (mp3/wav)
        stt_response = await stt.transcribe_bytes(bytes(audio_buffer), file_ext="mp3")
        user_text = stt_response.text

        # 2. Chat (Tsundere)
        chat_request = ChatRequest(text=user_text)
        chat_response = await chat.chat_with_persona(chat_request)

        # 3. Return Response
        return audio_pb2.AudioResponse(text=chat_response.text)

async def serve_grpc():
    server = grpc.aio.server()
    audio_pb2_grpc.add_SpeechServiceServicer_to_server(SpeechService(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC Server running on port 50051...")
    await server.start()
    await server.wait_for_termination()
