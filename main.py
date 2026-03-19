#!/usr/bin/env python3
"""
OpenAI-Compatible Audio/Speech Server for MiMo V2 TTS

This server provides an OpenAI-compatible `/v1/audio/speech` endpoint
that proxies requests to the Xiaomi MiMo V2 TTS API.

Usage:
    python main.py

API Endpoint:
    POST /v1/audio/speech

Example request:
    curl -X POST http://localhost:8000/v1/audio/speech \
      -H "Authorization: Bearer any-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "mimo-v2-tts",
        "input": "Hello, world!",
        "voice": "mimo_default",
        "response_format": "wav"
      }'
"""

import os
import base64
import io
from typing import Optional, Literal
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header, status
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MIMO_API_KEY = os.getenv("MIMO_API_KEY")
MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")

if not MIMO_API_KEY:
    raise RuntimeError(
        "MIMO_API_KEY environment variable is required. "
        "Please set it in your .env file or environment."
    )

# Initialize MiMo TTS client
mimo_client: Optional[OpenAI] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global mimo_client
    mimo_client = OpenAI(
        api_key=MIMO_API_KEY,
        base_url=MIMO_BASE_URL
    )
    print(f"✓ Connected to MiMo TTS API at {MIMO_BASE_URL}")
    yield
    print("✓ Shutting down server")


app = FastAPI(
    title="MiMo TTS OpenAI-Compatible Server",
    description="OpenAI-compatible audio/speech endpoint for Xiaomi MiMo V2 TTS",
    version="1.0.0",
    lifespan=lifespan
)


# Request/Response Models
class SpeechRequest(BaseModel):
    """OpenAI-compatible speech request model."""
    model: str = Field(
        default="mimo-v2-tts",
        description="The TTS model to use"
    )
    input: str = Field(
        ...,
        description="The text to generate audio for",
        max_length=4096
    )
    voice: str = Field(
        default="mimo_default",
        description="The voice to use for generation"
    )
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = Field(
        default="wav",
        description="The format of the audio output"
    )
    speed: float = Field(
        default=1.0,
        ge=0.25,
        le=4.0,
        description="The speed of the generated audio"
    )
    style: Optional[str] = Field(
        default=None,
        description="Speaking style (e.g., '粵語' for Cantonese)"
    )


class ErrorResponse(BaseModel):
    """Error response model."""
    error: dict


# Content type mapping
CONTENT_TYPE_MAP = {
    "mp3": "audio/mpeg",
    "opus": "audio/opus",
    "aac": "audio/aac",
    "flac": "audio/flac",
    "wav": "audio/wav",
    "pcm": "audio/pcm",
}


@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "name": "MiMo TTS OpenAI-Compatible Server",
        "version": "1.0.0",
        "endpoints": {
            "speech": "/v1/audio/speech",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "mimo_api_connected": mimo_client is not None}


@app.post("/v1/audio/speech")
async def create_speech(
    request: SpeechRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Generate speech from text using MiMo V2 TTS.
    
    This endpoint is compatible with OpenAI's `/v1/audio/speech` API.
    
    Args:
        request: Speech generation parameters
        authorization: API key (optional, for OpenAI compatibility)
    
    Returns:
        Audio file in the requested format
    """
    try:
        # Build messages for MiMo TTS API
        # The assistant's message content is what gets spoken
        # Add style tag if specified (e.g., [style:粵語] for Cantonese)
        text_to_speak = request.input
        voice = request.voice
        
        if request.style:
            text_to_speak = f"[style:{request.style}]{request.input}"
            # Use default_zh voice for Chinese styles for better pronunciation
            if request.style in ("粵語", "广东话", "廣東話", "广州话") and voice == "mimo_default":
                voice = "default_zh"
        
        messages = [
            {
                "role": "user",
                "content": "Hi"
            },
            {
                "role": "assistant",
                "content": text_to_speak
            }
        ]
        
        # Call MiMo TTS API
        completion = mimo_client.chat.completions.create(
            model=request.model,
            messages=messages,
            audio={
                "format": request.response_format,
                "voice": voice
            }
        )
        
        # Extract audio data from response
        if not completion.choices:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No audio data received from MiMo TTS API"
            )
        
        message = completion.choices[0].message
        
        # Check for audio data in the response
        if hasattr(message, 'audio') and message.audio:
            audio_data = message.audio.data
        elif isinstance(message.model_dump(), dict) and 'audio' in message.model_dump():
            audio_data = message.model_dump()['audio']['data']
        else:
            # Fallback: check completion raw response
            completion_dict = completion.model_dump()
            if 'choices' in completion_dict and completion_dict['choices']:
                audio_info = completion_dict['choices'][0].get('message', {}).get('audio', {})
                audio_data = audio_info.get('data', '')
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Audio data not found in MiMo TTS response"
                )
        
        # Decode base64 audio data
        try:
            audio_bytes = base64.b64decode(audio_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to decode audio data: {str(e)}"
            )
        
        # Return audio response
        content_type = CONTENT_TYPE_MAP.get(request.response_format, "audio/wav")
        
        return Response(
            content=audio_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename=speech.{request.response_format}"
            }
        )
        
    except Exception as e:
        # Handle specific OpenAI/MiMo errors
        error_msg = str(e)
        
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MiMo API key"
            )
        elif "rate limit" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        elif isinstance(e, HTTPException):
            raise
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"TTS generation failed: {error_msg}"
            )


# OpenAI compatibility: also support the chat completions endpoint
@app.post("/v1/chat/completions")
async def chat_completions(
    request: dict,
    authorization: Optional[str] = Header(None)
):
    """
    Proxy to MiMo V2 TTS chat completions endpoint.
    
    This provides full OpenAI compatibility for chat-based TTS requests.
    """
    try:
        completion = mimo_client.chat.completions.create(**request)
        return completion.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI compatibility)."""
    return {
        "object": "list",
        "data": [
            {
                "id": "mimo-v2-tts",
                "object": "model",
                "created": 1704067200,
                "owned_by": "xiaomi-mimo"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           MiMo TTS OpenAI-Compatible Server                  ║
╠══════════════════════════════════════════════════════════════╣
║  Endpoint: http://{host}:{port:<5}                           ║
║  Speech API: http://{host}:{port}/v1/audio/speech            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host=host, port=port)
