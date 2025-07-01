"""
TTS API Example
Demonstrates how to use the GPT-SoVITS TTS API endpoints
"""

import os
import json
import shutil
from gradio_client import Client, handle_file

def load_config(config_path="config.json"):
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in config file '{config_path}'")
        return None

def main():
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Initialize the client
    client = Client(config["api_url"])
    
    print("=== TTS API Example ===\n")
    
    # Check if reference audio exists
    ref_audio_path = config["reference_audio"]["file_path"]
    if not os.path.exists(ref_audio_path):
        print(f"Warning: Reference audio file not found at {ref_audio_path}")
        print("Please check the file path in config.json")
        return
    
    print(f"Using reference audio: {ref_audio_path}")
    print(f"Reference text: {config['reference_audio']['text']}")
    print()
    
    # Get text input from user
    text_to_synthesize = input("请输入要合成的文本: ").strip()
    if not text_to_synthesize:
        print("No text provided, exiting.")
        return
    
    print(f"\nGenerating TTS for: {text_to_synthesize}")
    
    try:
        tts_result = client.predict(
            ref_wav_path=handle_file(ref_audio_path),
            prompt_text=config["reference_audio"]["text"],
            prompt_language=config["reference_audio"]["language"],
            text=text_to_synthesize,
            text_language=config["tts_settings"]["text_language"],
            how_to_cut=config["tts_settings"]["how_to_cut"],
            top_k=config["tts_settings"]["top_k"],
            top_p=config["tts_settings"]["top_p"],
            temperature=config["tts_settings"]["temperature"],
            ref_free=config["tts_settings"]["ref_free"],
            speed=config["tts_settings"]["speed"],
            if_freeze=config["tts_settings"]["if_freeze"],
            inp_refs=None,
            sample_steps=config["tts_settings"]["sample_steps"],
            if_sr=config["tts_settings"]["if_sr"],
            pause_second=config["tts_settings"]["pause_second"],
            api_name="/get_tts_wav"
        )
        
        print("TTS audio generated successfully!")
        print(f"Output audio file: {tts_result}")
        
        # Copy the generated audio to current directory
        if os.path.exists(tts_result):
            print(f"Audio file size: {os.path.getsize(tts_result)} bytes")
            
            output_filename = config["output"]["filename"]
            shutil.copy2(tts_result, output_filename)
            print(f"Audio saved as: {os.path.abspath(output_filename)}")
        else:
            print("Warning: Generated audio file not found")
        
    except Exception as e:
        print(f"Error generating TTS audio: {e}")

if __name__ == "__main__":
    main()
