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

```bash
python main.py
```

The server will start on `http://localhost:8000`.

## 📖 Usage Examples

### English TTS

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello, world!",
    "response_format": "wav"
  }' \
  --output speech.wav
```

### Cantonese TTS (广东话)

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "早晨，食咗飯未呀？",
    "response_format": "wav",
    "style": "广东话"
  }' \
  --output cantonese.wav
```

### Using Python (OpenAI SDK)

```python
import httpx

response = httpx.post(
    "http://localhost:8000/v1/audio/speech",
    json={
        "input": "早晨，食咗飯未呀？",
        "response_format": "wav",
        "style": "广东话"  # Enable Cantonese
    }
)

with open("cantonese.wav", "wb") as f:
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
| `voice` | string | No | Voice identifier (default: `mimo_default`) |
| `response_format` | string | No | Audio format: `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm` (default: `wav`) |
| `speed` | float | No | Playback speed 0.25-4.0 (default: `1.0`) |
| `style` | string | No | Speaking style, e.g., `广东话` for Cantonese |

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
