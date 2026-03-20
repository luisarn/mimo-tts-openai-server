# MiMo V2 TTS OpenAI-Compatible Server

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A FastAPI-based server that provides an **OpenAI-compatible** `/v1/audio/speech` endpoint, proxying requests to the **Xiaomi MiMo V2 Text-to-Speech (TTS) API**.

## 🌟 Features

- 🎯 **OpenAI API Compatible** - Drop-in replacement for OpenAI's TTS endpoint
- 🗣️ **Multi-language Support** - English, Mandarin Chinese, and **Cantonese (广东话)**
- 🎨 **Speaking Styles** - Configure dialects and moods via the `style` parameter
- 🔊 **Multiple Formats** - wav, mp3, opus, aac, flac, pcm
- ⚡ **Fast & Lightweight** - Built with FastAPI and async support
- 🔧 **Easy Integration** - Works with the official OpenAI Python SDK

## 🚀 Quick Start

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

Using `uv` (recommended):
```bash
uv run uvicorn server:app --reload --host 0.0.0.0 --port 8500
```

Or using Python directly:
```bash
python server.py
```

The server will start on `http://localhost:8500`.

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8500 (Press CTRL+C to quit)
```

### 4. Test the Server

Health check:
```bash
curl http://localhost:8500/health
```

Test TTS generation:
```bash
curl -X POST http://localhost:8500/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, world!"}' \
  --output test.mp3
```

## 🖥️ Running the Server

### Start the Server

Using `uv` (recommended with auto-reload):
```bash
uv run uvicorn server:app --reload --host 0.0.0.0 --port 8500
```

Or using Python directly:
```bash
python server.py
```

By default, the server runs on `http://0.0.0.0:8500`. You can customize the host and port:

```bash
# Using uvicorn
uv run uvicorn server:app --host 127.0.0.1 --port 8080

# Or using environment variables
HOST=127.0.0.1 PORT=8080 python server.py
```

### Server Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | Server info | Server status and available endpoints |
| `GET /health` | Health check | Check server and MiMo API connection |
| `GET /v1/models` | List models | OpenAI-compatible models endpoint |
| `POST /v1/audio/speech` | TTS | Text-to-speech generation (OpenAI-compatible) |
| `POST /v1/chat/completions` | Chat | Direct proxy to MiMo chat completions |

### Default Settings

The `/v1/audio/speech` endpoint uses these defaults:

```json
{
  "model": "mimo-v2-tts",
  "voice": "default_zh",
  "response_format": "mp3",
  "speed": 1.0,
  "style": "粵語"
}
```

This means **Cantonese TTS is the default**. For English or other languages, you may want to use `voice: "mimo_default"`.

## 📖 Usage Examples

### English TTS

```bash
curl -X POST http://localhost:8500/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello, world!",
    "response_format": "wav"
  }' \
  --output speech.wav
```

### Cantonese TTS (广东话)

```bash
curl -X POST http://localhost:8500/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "早晨，食咗飯未呀？",
    "response_format": "wav",
    "style": "广东话"
  }' \
  --output cantonese.wav
```

### Using Python (OpenAI SDK)

The server is fully compatible with the official OpenAI Python SDK:

```python
from openai import OpenAI

client = OpenAI(
    api_key="any-key",  # Not validated locally
    base_url="http://localhost:8500/v1"
)

# Generate speech (uses default Cantonese settings)
response = client.audio.speech.create(
    model="mimo-v2-tts",
    voice="default_zh",
    input="早晨，食咗飯未呀？"
)

response.stream_to_file("output.mp3")
```

Or using `httpx` for direct HTTP requests:

```python
import httpx

response = httpx.post(
    "http://localhost:8500/v1/audio/speech",
    json={
        "input": "早晨，食咗飯未呀？",
        "response_format": "mp3",
        "style": "粵語"  # Enable Cantonese
    }
)

with open("cantonese.mp3", "wb") as f:
    f.write(response.content)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | Server info | List available endpoints |
| `GET /health` | Health check | Check server and MiMo API status |
| `GET /v1/models` | List models | OpenAI-compatible models endpoint |
| `POST /v1/audio/speech` | TTS | Text-to-speech generation |
| `POST /v1/chat/completions` | Chat | Direct proxy to MiMo chat completions |

## Request Format

### POST /v1/audio/speech

```json
{
  "model": "mimo-v2-tts",
  "input": "Text to convert to speech",
  "voice": "mimo_default",
  "response_format": "wav",
  "speed": 1.0,
  "style": "广东话"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | TTS model to use (default: `mimo-v2-tts`) |
| `input` | string | Yes | Text to convert (max 4096 chars) |
| `voice` | string | No | Voice identifier (default: `default_zh`) |
| `response_format` | string | No | Audio format: `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm` (default: `mp3`) |
| `speed` | float | No | Playback speed 0.25-4.0 (default: `1.0`) |
| `style` | string | No | Speaking style, e.g., `粵語` for Cantonese (default: `粵語`) |

### Cantonese TTS

To generate Cantonese speech, add the `style` parameter with value `广东话`:

```bash
curl -X POST http://localhost:8500/v1/audio/speech \
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

**Note:** The server defaults to Cantonese TTS with `default_zh` voice and `粵語` style. For other languages, set `style` to `null` or use the `mimo_default` voice.

Or using Python:

```python
import httpx

response = httpx.post(
    "http://localhost:8500/v1/audio/speech",
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
| `MIMO_API_KEY` | - | Your MiMo API key from https://platform.xiaomimimo.com |
| `MIMO_BASE_URL` | `https://api.xiaomimimo.com/v1` | MiMo API base URL |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |

## Testing

### Cantonese Phrases Test

Test 8 common Cantonese phrases:

```bash
python test_cantonese.py all
```

Phrases include:
- 你好，歡迎使用小米語音合成系統。
- 多謝你嘅支持，我會繼續努力。
- 你食咗飯未呀？今日過得好唔好？
- 早晨！希望你今日有美好嘅一日。
- 今日天氣好好，好適合去公園散步。
- 廣東菜真係好好食，我最鍾意飲茶。
- 呢件衫幾錢？可唔可以平啲？
- 請問車站喺邊度？點樣去最快？

### Interactive Mode

Type your own Cantonese text:

```bash
python test_cantonese.py interactive
```

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

The server translates OpenAI's `/audio/speech` format to MiMo's chat completion format internally, handling base64 decoding and returning raw audio bytes.

## Project Structure

```
.
├── main.py              # FastAPI server implementation
├── client_example.py    # Example client usage with OpenAI SDK
├── test_cantonese.py    # Cantonese TTS testing script
├── requirements.txt     # Python dependencies
├── .env.example         # Environment configuration template
└── README.md            # This file
```

## MiMo V2 TTS API Reference

Official documentation: https://platform.xiaomimimo.com/#/docs/api/chat/openai-api

## License

MIT License
