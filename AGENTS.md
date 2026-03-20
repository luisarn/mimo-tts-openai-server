# MiMo V2 TTS OpenAI-Compatible Server

## Project Overview

This is a **FastAPI-based server** that provides an OpenAI-compatible `/v1/audio/speech` endpoint, acting as a proxy to the **Xiaomi MiMo V2 Text-to-Speech (TTS) API**.

The server translates OpenAI-style TTS requests into MiMo's chat-completion-based TTS API calls, allowing developers to use the official OpenAI SDK with the MiMo TTS service.

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Your Client   │────▶│   This Server    │────▶│  MiMo V2 TTS    │
│  (OpenAI SDK)   │     │  (FastAPI proxy) │     │     API         │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                        │                       │
         │                /v1/audio/speech          chat.completions
         │                (OpenAI format)          (MiMo format)
         │                        │                       │
         │◄───────────────────────┘◄──────────────────────┘
         │                    Audio file (bytes)
         │
    Audio playback
```

## Technology Stack

- **Language**: Python 3.8+
- **Web Framework**: FastAPI
- **Server**: Uvicorn (ASGI)
- **API Client**: OpenAI Python SDK
- **Data Validation**: Pydantic v2
- **Environment**: python-dotenv

## Project Structure

```
/Users/luis/Workspace/xiaomi-mimo-v2-tts-server/
├── main.py              # FastAPI server implementation
├── client_example.py    # Example client usage with OpenAI SDK
├── test_cantonese.py    # Cantonese TTS testing script
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── README.md            # Human-readable documentation
├── AGENTS.md            # This file - AI agent documentation
└── test_output/         # Generated audio files from tests
```

## Setup and Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `fastapi>=0.104.0`
- `uvicorn[standard]>=0.24.0`
- `openai>=1.0.0`
- `pydantic>=2.0.0`
- `python-dotenv>=1.0.0`

### 2. Configure Environment

Copy the example environment file and add your MiMo API key:

```bash
cp .env.example .env
# Edit .env and set your MIMO_API_KEY
```

**Required Environment Variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MIMO_API_KEY` | Yes | - | Your MiMo API key from https://platform.xiaomimimo.com |
| `MIMO_BASE_URL` | No | `https://api.xiaomimimo.com/v1` | MiMo API base URL |
| `HOST` | No | `0.0.0.0` | Server bind address |
| `PORT` | No | `8000` | Server port |

### 3. Start the Server

```bash
python main.py
```

The server will start on `http://localhost:8500` (or your configured HOST:PORT).

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | Root | Server info and available endpoints |
| `GET /health` | Health | Health check with MiMo API connection status |
| `GET /v1/models` | Models | List available models (OpenAI-compatible) |
| `POST /v1/audio/speech` | TTS | Text-to-speech generation (OpenAI-compatible) |
| `POST /v1/chat/completions` | Chat | Direct proxy to MiMo chat completions |

### POST /v1/audio/speech

OpenAI-compatible speech generation endpoint.

**Request Body:**

```json
{
  "model": "mimo-v2-tts",
  "input": "Text to convert to speech",
  "voice": "mimo_default",
  "response_format": "wav",
  "speed": 1.0
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | No | TTS model (default: `mimo-v2-tts`) |
| `input` | string | Yes | Text to convert (max 4096 chars) |
| `voice` | string | No | Voice identifier (default: `mimo_default`) |
| `response_format` | string | No | Audio format: `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm` (default: `wav`) |
| `speed` | float | No | Playback speed 0.25-4.0 (default: `1.0`) |

**Response:** Audio file bytes in the requested format.

## Usage Examples

### Using cURL

```bash
curl -X POST http://localhost:8500/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mimo-v2-tts",
    "input": "Hello, world!",
    "voice": "mimo_default",
    "response_format": "wav"
  }' \
  --output speech.wav
```

### Using Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    api_key="local-server-no-key-needed",
    base_url="http://localhost:8500/v1"
)

response = client.audio.speech.create(
    model="mimo-v2-tts",
    voice="mimo_default",
    input="Hello from MiMo TTS!",
    response_format="wav"
)

response.stream_to_file("output.wav")
```

### Run Client Examples

```bash
# List available models
python client_example.py models

# Simple TTS generation
python client_example.py simple

# Chat completion with audio
python client_example.py chat

# Run all examples
python client_example.py
```

### Cantonese TTS Testing

```bash
# Test all Cantonese phrases
python test_cantonese.py all

# Test without auto-playback
python test_cantonese.py all --no-play

# Interactive mode
python test_cantonese.py interactive

# Test single phrase (index 0-7)
python test_cantonese.py single --phrase 0
```

## Code Style Guidelines

- **Language**: Python 3.8+ with type hints
- **Formatting**: 4-space indentation
- **Docstrings**: Use triple quotes for module and function documentation
- **Imports**: Group standard library, third-party, and local imports
- **Error Handling**: Use try-except blocks with specific error messages
- **Models**: Use Pydantic BaseModel for request/response validation

## Testing Strategy

The project uses manual/integration testing rather than automated unit tests:

1. **client_example.py**: Demonstrates various API usage patterns
   - Simple TTS generation
   - Streaming audio
   - Chat completion with audio
   - Model listing

2. **test_cantonese.py**: Specialized testing for Cantonese TTS
   - 8 common Cantonese phrases with Jyutping pronunciation
   - Auto-playback support (macOS: afplay, Linux: paplay/aplay, Windows: winsound)
   - Interactive mode for custom text testing

3. **Manual cURL testing**: Direct API endpoint verification

## Security Considerations

- **API Key Management**: Never commit the `.env` file containing `MIMO_API_KEY`. The `.env.example` file is provided as a template.
- **Local Server**: The local server does not validate the Authorization header (accepts any key for OpenAI SDK compatibility).
- **HTTPS**: The MiMo API endpoint uses HTTPS for secure communication.
- **Audio Data**: Audio data from MiMo API is base64-encoded and decoded before being returned to the client.

## Important Implementation Details

### TTS to Chat Completion Mapping

The server maps OpenAI's `/v1/audio/speech` endpoint to MiMo's chat completions API:

```python
messages = [
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": request.input}  # This text gets spoken
]
```

The `input` text from the speech request is placed in the assistant's message content, which MiMo TTS then converts to speech.

### Audio Format Mapping

| OpenAI Format | Content-Type | Notes |
|---------------|--------------|-------|
| `wav` | `audio/wav` | Default format |
| `mp3` | `audio/mpeg` | Compressed audio |
| `opus` | `audio/opus` | Low latency |
| `aac` | `audio/aac` | Apple format |
| `flac` | `audio/flac` | Lossless compression |
| `pcm` | `audio/pcm` | Raw PCM data |

## Official Documentation

- MiMo V2 TTS API: https://platform.xiaomimimo.com/#/docs/api/chat/openai-api

## License

MIT License
