#!/usr/bin/env python3
"""
Test script for Cantonese TTS using the MiMo OpenAI-Compatible Server.

This script generates audio for common Cantonese phrases and plays them.
"""

import os
import sys
import subprocess
import time
from openai import OpenAI

# Configure client
client = OpenAI(
    api_key="local-server-no-key-needed",
    base_url="http://localhost:8500/v1"
)

# Common Cantonese phrases for testing
CANTONESE_PHRASES = [
    {
        "name": "greeting",
        "text": "你好，歡迎使用小米語音合成系統。",
        "pinyin": "nei5 hou2, fun1 jing4 sei6 jung6 siu2 mai5 jyu5 jam1 hap6 sing4 hai6 tung2."
    },
    {
        "name": "thank_you",
        "text": "多謝你嘅支持，我會繼續努力。",
        "pinyin": "do1 ze6 nei5 ge3 zi1 ci4, ngo5 wui5 gai3 zuk6 nou5 lik6."
    },
    {
        "name": "how_are_you",
        "text": "你食咗飯未呀？今日過得好唔好？",
        "pinyin": "nei5 sik6 zo2 faan6 mei6 aa3? gam1 jat6 gwo3 dak1 hou2 m4 hou2?"
    },
    {
        "name": "good_morning",
        "text": "早晨！希望你今日有美好嘅一日。",
        "pinyin": "zou2 san4! hei1 mong6 nei5 gam1 jat6 jau5 mei5 hou2 ge3 jat1 jat6."
    },
    {
        "name": "weather",
        "text": "今日天氣好好，好適合去公園散步。",
        "pinyin": "gam1 jat6 tin1 hei3 hou2 hou2, hou2 sik1 hap6 heoi3 gung1 jyun4 saan3 bou6."
    },
    {
        "name": "food",
        "text": "廣東菜真係好好食，我最鍾意飲茶。",
        "pinyin": "gwong2 dung1 coi3 zan1 hai6 hou2 hou2 sik6, ngo5 zeoi3 zung1 ji3 jam2 caa4."
    },
    {
        "name": "shopping",
        "text": "呢件衫幾錢？可唔可以平啲？",
        "pinyin": "ni1 gin6 saam1 gei2 cin2? ho2 m4 ho2 ji5 peng4 di1?"
    },
    {
        "name": "directions",
        "text": "請問車站喺邊度？點樣去最快？",
        "pinyin": "ceng2 man6 ce1 zaam6 hai2 bin1 dou6? dim2 joeng2 heoi3 zeoi3 faai3?"
    },
]

def play_audio(file_path):
    """Play audio file using system player."""
    system = sys.platform
    
    try:
        if system == "darwin":  # macOS
            subprocess.run(["afplay", file_path], check=True)
        elif system == "linux":
            # Try different Linux players
            for player in ["paplay", "aplay", "mpg123", "ffplay", "cvlc"]:
                if subprocess.run(["which", player], capture_output=True).returncode == 0:
                    if player == "ffplay":
                        subprocess.run([player, "-nodisp", "-autoexit", file_path], 
                                     check=True, stderr=subprocess.DEVNULL)
                    else:
                        subprocess.run([player, file_path], check=True)
                    break
        elif system == "win32":  # Windows
            import winsound
            winsound.PlaySound(file_path, winsound.SND_FILENAME)
        else:
            print(f"⚠️  Automatic playback not supported on {system}")
            print(f"   Please play {file_path} manually")
            return False
        return True
    except Exception as e:
        print(f"⚠️  Could not play audio: {e}")
        print(f"   File saved at: {file_path}")
        return False


def generate_speech(text, output_file, voice="mimo_default", format="mp3", style=None):
    """Generate speech using the local TTS server."""
    try:
        # Use raw HTTP request to support extra parameters like 'style'
        import httpx
        response = httpx.post(
            "http://localhost:8500/v1/audio/speech",
            json={
                "model": "mimo-v2-tts",
                "input": text,
                "voice": voice,
                "response_format": format,
                "style": style
            },
            timeout=60.0
        )
        response.raise_for_status()
        with open(output_file, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"❌ Error generating speech: {e}")
        return False


def test_single_phrase(phrase, output_dir="test_output", auto_play=True, style=None):
    """Test a single Cantonese phrase."""
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"{phrase['name']}.mp3")
    
    print(f"\n📝 Phrase: {phrase['name']}")
    print(f"   Text: {phrase['text']}")
    print(f"   Pinyin: {phrase['pinyin']}")
    if style:
        print(f"   Style: {style}")
    print(f"   Generating...", end=" ")
    
    if generate_speech(phrase['text'], output_file, style=style):
        print(f"✓ Saved to {output_file}")
        
        if auto_play:
            print(f"   Playing...", end=" ")
            if play_audio(output_file):
                print("✓")
            time.sleep(0.5)  # Small delay between phrases
    else:
        print("✗ Failed")


def test_all_phrases(auto_play=True, style="粤语 香港口音 开心热情 语速快"):
    """Test all Cantonese phrases."""
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("🎵 MiMo TTS Cantonese Test")
    if style:
        print(f"   Style: {style}")
    print("=" * 60)
    
    # Check server health
    print("\n📡 Checking server...", end=" ")
    try:
        import httpx
        response = httpx.get("http://localhost:8500/health")
        if response.status_code == 200:
            print("✓ Server is healthy")
        else:
            print("⚠️ Server returned non-200 status")
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        print("\nPlease start the server first:")
        print("   python main.py")
        return
    
    # Generate all phrases
    print(f"\n🎯 Testing {len(CANTONESE_PHRASES)} Cantonese phrases...")
    print("-" * 60)
    
    for i, phrase in enumerate(CANTONESE_PHRASES, 1):
        print(f"\n[{i}/{len(CANTONESE_PHRASES)}]")
        test_single_phrase(phrase, output_dir, auto_play, style=style)
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print(f"📁 Audio files saved in: {output_dir}/")
    print("=" * 60)


def interactive_mode():
    """Interactive mode for custom text."""
    print("\n🎤 Interactive Cantonese TTS Mode")
    print("Type your Cantonese text (or 'quit' to exit):")
    print("-" * 40)
    
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    counter = 1
    while True:
        try:
            text = input(f"\n[{counter}] > ").strip()
            
            if text.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not text:
                continue
            
            output_file = os.path.join(output_dir, f"custom_{counter:03d}.mp3")
            
            print(f"   Generating...", end=" ")
            if generate_speech(text, output_file):
                print(f"✓ Saved to {output_file}")
                print(f"   Playing...", end=" ")
                if play_audio(output_file):
                    print("✓")
            else:
                print("✗ Failed")
            
            counter += 1
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MiMo TTS with Cantonese phrases")
    parser.add_argument("mode", nargs="?", default="all", 
                       choices=["all", "single", "interactive"],
                       help="Test mode: all phrases, single phrase, or interactive")
    parser.add_argument("--no-play", action="store_true",
                       help="Generate audio without playing")
    parser.add_argument("--phrase", type=int, default=0,
                       help="Phrase index for single mode (0-7)")
    
    args = parser.parse_args()
    
    auto_play = not args.no_play
    
    if args.mode == "all":
        test_all_phrases(auto_play=auto_play)
    elif args.mode == "single":
        if 0 <= args.phrase < len(CANTONESE_PHRASES):
            test_single_phrase(CANTONESE_PHRASES[args.phrase], auto_play=auto_play)
        else:
            print(f"Invalid phrase index. Choose 0-{len(CANTONESE_PHRASES)-1}")
    elif args.mode == "interactive":
        interactive_mode()
