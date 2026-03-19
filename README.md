# MiMo V2 TTS OpenAI-Compatible Server

A FastAPI-based server that provides an OpenAI-compatible `/v1/audio/speech` endpoint, proxying requests to the **Xiaomi MiMo V2 Text-to-Speech API**.

## Features

- ✅ **OpenAI-compatible** `/v1/audio/speech` endpoint
- ✅ **Full OpenAI SDK support** - use the official `openai` Python library
- ✅ **Multiple audio formats** - mp3, wav, opus, aac, flac, pcm
- ✅ **Streaming support** for audio responses
- ✅ **Chat completions endpoint** for direct MiMo API access
- ✅ **Health check and model listing** endpoints

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and add your MiMo API key:

```bash
cp .env.example .env
# Edit .env and set your MIMO_API_KEY
```

### 3. Start the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server info |
| `/health` | GET | Health check |
| `/v1/models` | GET | List available models |
| `/v1/audio/speech` | POST | Text-to-speech generation |
| `/v1/chat/completions` | POST | Chat completion with audio |

## Usage Examples

### Using cURL

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
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
    base_url="http://localhost:8000/v1"
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

## Request Format

### POST /v1/audio/speech

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
| `model` | string | Yes | TTS model to use (default: `mimo-v2-tts`) |
| `input` | string | Yes | Text to convert (max 4096 chars) |
| `voice` | string | No | Voice identifier (default: `mimo_default`) |
| `response_format` | string | No | Audio format: `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm` (default: `wav`) |
| `speed` | float | No | Playback speed 0.25-4.0 (default: `1.0`) |
| `style` | string | No | Speaking style, e.g., `粵語` for Cantonese |

### Cantonese TTS

To generate Cantonese speech, add the `style` parameter with value `广东话`:

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mimo-v2-tts",
    "input": "早晨，食咗飯未呀？",
    "voice": "mimo_default",
    "response_format": "wav",
    "style": "广东话"
  }' \
  --output cantonese.wav
```

**Note:** When `style` is set to a Chinese dialect like `广东话` (Cantonese), the server automatically uses the `default_zh` voice for better pronunciation quality.

Or using Python:

```python
import httpx

response = httpx.post(
    "http://localhost:8000/v1/audio/speech",
    json={
        "model": "mimo-v2-tts",
        "input": "早晨，食咗飯未呀？",
        "voice": "mimo_default",
        "response_format": "wav",
        "style": "广东话"  # Enable Cantonese
    }
)

with open("cantonese.wav", "wb") as f:
    f.write(response.content)
```

**Supported Style Values:**
- `广东话` - Cantonese (Guangdong dialect) - **Recommended**
- `粵語` - Alternative Cantonese spelling
- `廣東話` - Traditional characters (may have accent)

## Configuration

Environment variables (set in `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `MIMO_API_KEY` | *required* | Your MiMo API key |
| `MIMO_BASE_URL` | `https://api.xiaomimimo.com/v1` | MiMo API base URL |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |

## Architecture

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

## Project Structure

```
.
├── main.py              # FastAPI server implementation
├── client_example.py    # Example client usage
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── README.md            # This file
```

## MiMo V2 TTS API Reference

Official documentation: https://platform.xiaomimimo.com/#/docs/api/chat/openai-api

## License

MIT License
