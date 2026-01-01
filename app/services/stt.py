import os
import uuid
import time
import asyncio
import json
import boto3
import requests
from fastapi import UploadFile
from app.schemas.intelligence import STTResponse
from app.core.config import get_settings

settings = get_settings()

async def transcribe_audio(file: UploadFile) -> STTResponse:
    """
    HTTP Wrapper: Transcribes UploadFile.
    """
    file_content = await file.read()
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else "mp3"
    return await transcribe_bytes(file_content, file_ext)

async def transcribe_bytes(file_content: bytes, file_ext: str = "mp3") -> STTResponse:
    """
    Core Logic: Uploads bytes to S3 and calls Transcribe.
    """
    try:
        bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
        if not bucket_name:
            return STTResponse(text="Configuration Error: AWS_S3_BUCKET_NAME is missing.")

        s3_client = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        transcribe_client = boto3.client(
            'transcribe',
            region_name=settings.AWS_S3_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

        job_name = f"jiaa-stt-{uuid.uuid4()}"
        s3_key = f"temp-audio/{job_name}.{file_ext}"

        # 1. Upload to S3
        s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=file_content)

        job_uri = f"s3://{bucket_name}/{s3_key}"

        # 2. Start Transcription Job
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat=file_ext if file_ext in ['mp3', 'mp4', 'wav', 'flac'] else 'mp3',
            LanguageCode='ko-KR'
        )

        # 3. Poll for Completion
        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            
            if job_status in ['COMPLETED', 'FAILED']:
                break
            
            await asyncio.sleep(1)

        if job_status == 'COMPLETED':
            # 4. Get Result
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            response = requests.get(transcript_uri)
            data = response.json()
            transcript_text = data['results']['transcripts'][0]['transcript']
            
            # s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
            return STTResponse(text=transcript_text)
        else:
            return STTResponse(text="Transcription Failed at AWS side.")

    except Exception as e:
        print(f"AWS Transcribe Error: {e}")
        return STTResponse(text=f"Error: {str(e)}")
