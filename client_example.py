#!/usr/bin/env python3
"""
Example client for the MiMo TTS OpenAI-Compatible Server.

This demonstrates how to use the local server with the OpenAI client library.
"""

import os
from openai import OpenAI

# Configure the client to use the local server
client = OpenAI(
    api_key="local-server-no-key-needed",  # The local server doesn't validate this
    base_url="http://localhost:8500/v1"
)

def text_to_speech_simple():
    """Basic text-to-speech example."""
    print("Generating speech...")
    
    response = client.audio.speech.create(
        model="mimo-v2-tts",
        voice="mimo_default",
        input="Hello! This is a test of the MiMo V2 text-to-speech system.",
        response_format="wav"
    )
    
    # Save the audio file
    output_file = "output.wav"
    response.stream_to_file(output_file)
    print(f"✓ Audio saved to {output_file}")
    return output_file


def text_to_speech_streaming():
    """Streaming text-to-speech example."""
    print("Generating speech (streaming)...")
    
    response = client.audio.speech.create(
        model="mimo-v2-tts",
        voice="mimo_default",
        input="This is a streaming test of the MiMo TTS system.",
        response_format="mp3"
    )
    
    # Stream to file
    output_file = "output_streaming.mp3"
    with open(output_file, "wb") as f:
        for chunk in response.iter_bytes(chunk_size=8192):
            f.write(chunk)
    
    print(f"✓ Audio saved to {output_file}")
    return output_file


def chat_completion_with_audio():
    """Direct chat completion with audio output."""
    print("Generating audio via chat completions...")
    
    completion = client.chat.completions.create(
        model="mimo-v2-tts",
        messages=[
            {"role": "user", "content": "Tell me a short joke about programming."},
            {"role": "assistant", "content": "..."}
        ],
        audio={
            "format": "wav",
            "voice": "mimo_default"
        }
    )
    
    print("Response:", completion.model_dump_json(indent=2))
    return completion


def list_available_models():
    """List available models on the server."""
    models = client.models.list()
    print("Available models:")
    for model in models.data:
        print(f"  - {model.id}")
    return models


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "simple":
            text_to_speech_simple()
        elif command == "streaming":
            text_to_speech_streaming()
        elif command == "chat":
            chat_completion_with_audio()
        elif command == "models":
            list_available_models()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: simple, streaming, chat, models")
    else:
        # Run all examples
        print("=" * 50)
        list_available_models()
        print("=" * 50)
        text_to_speech_simple()
        print("=" * 50)
        chat_completion_with_audio()
