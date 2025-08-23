#!/usr/bin/env python3
"""
Test script to debug dialogue generation with GPT-4.1
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

async def test_dialogue_generation():
    """Test dialogue generation with different prompts"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("DEFAULT_MODEL", "gpt-4.1")
    
    print(f"Testing dialogue generation with {model}")
    print("=" * 60)
    
    # Test prompt 1: Simple format
    prompt1 = """
    Generate exactly 3 lines of dialogue between Alex and Sam.
    
    Context: They are discussing an ethical dilemma about AI.
    
    Return ONLY a JSON array, nothing else:
    [
        {"speaker": "Alex", "line": "dialogue text"},
        {"speaker": "Sam", "line": "dialogue text"},
        {"speaker": "Alex", "line": "dialogue text"}
    ]
    """
    
    print("\n📝 Test 1: Simple JSON array format")
    print("-" * 40)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a screenwriter. Return only valid JSON."},
                {"role": "user", "content": prompt1}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        print(f"Raw response:\n{content}\n")
        
        # Try to parse
        try:
            parsed = json.loads(content)
            print(f"✅ Successfully parsed: {len(parsed)} dialogue entries")
            for entry in parsed[:2]:
                print(f"  - {entry['speaker']}: {entry['line'][:50]}...")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
    
    # Test prompt 2: More specific format
    prompt2 = """
    Create dialogue for a scene about AI ethics.
    
    Characters:
    - Alex Chen: Ambitious developer
    - Sam Rodriguez: Ethical mentor
    - Jordan Park: Competitive rival
    
    Generate 5 lines of natural dialogue.
    
    IMPORTANT: Return as a JSON array with this exact structure:
    [{"speaker": "name", "line": "text"}, ...]
    
    No additional text, no markdown, just the JSON array.
    """
    
    print("\n📝 Test 2: More specific instructions")
    print("-" * 40)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Output only valid JSON arrays. No markdown, no extra text."},
                {"role": "user", "content": prompt2}
            ],
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"}  # Force JSON mode if supported
        )
        
        content = response.choices[0].message.content
        print(f"Raw response:\n{content}\n")
        
        # Try to parse
        try:
            # Handle if response is wrapped in an object
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "dialogue" in parsed:
                parsed = parsed["dialogue"]
            elif isinstance(parsed, dict):
                # Try to extract array from any key
                for key, value in parsed.items():
                    if isinstance(value, list):
                        parsed = value
                        break
            
            if isinstance(parsed, list):
                print(f"✅ Successfully parsed: {len(parsed)} dialogue entries")
                for entry in parsed[:3]:
                    if isinstance(entry, dict) and "speaker" in entry and "line" in entry:
                        print(f"  - {entry['speaker']}: {entry['line'][:50]}...")
            else:
                print(f"⚠️ Unexpected format: {type(parsed)}")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    print(f"✅ Extracted JSON via regex: {len(parsed)} entries")
                except:
                    print("❌ Regex extraction also failed")
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
        if "response_format" in str(e):
            print("Note: JSON response format may not be supported")

    print("\n" + "=" * 60)
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(test_dialogue_generation())