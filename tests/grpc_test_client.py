import asyncio
import grpc
import sys
import os

# Ensure app modules are found
sys.path.append(os.getcwd())

from app.protos import audio_pb2, audio_pb2_grpc

async def test_audio_stream():
    """
    Reads an audio file and streams it to the gRPC server.
    """
    # 1. Connect to Server
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = audio_pb2_grpc.SpeechServiceStub(channel)
        print("Connected to gRPC server at localhost:50051")

        # 2. Generator for Streaming Requests
        async def request_generator():
            # Send initial chunk (Simulation)
            chunk_size = 1024 * 16 # 16KB chunks
            
            # Use a dummy audio if no file exists, or prompt user
            # Here we just send dummy bytes to verify connectivity and error handling
            # If you have a real file, uncomment below:
            # with open("test_audio.mp3", "rb") as f:
            #     while True:
            #         data = f.read(chunk_size)
            #         if not data: break
            #         yield audio_pb2.AudioRequest(audio_data=data, is_final=False)
            
            print("Sending dummy audio bytes...")
            yield audio_pb2.AudioRequest(audio_data=b'FAKE_AUDIO_DATA_HEADER', is_final=False)
            await asyncio.sleep(0.1)
            yield audio_pb2.AudioRequest(audio_data=b'FAKE_AUDIO_DATA_BODY', is_final=True)
            print("Finished sending.")

        # 3. Call RPC
        try:
            response = await stub.SendAudioStream(request_generator())
            print(f"Server Response: {response.text}")
        except grpc.RpcError as e:
            print(f"gRPC Error: {e.code()} - {e.details()}")

if __name__ == "__main__":
    asyncio.run(test_audio_stream())
