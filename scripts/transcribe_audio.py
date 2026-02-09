#!/usr/bin/env python3
"""
Transcribe audio to text using Groq Whisper API
Usage: python3 transcribe_audio.py <audio_file> [--output OUTPUT_FILE] [--api-key API_KEY]
"""

import sys
import os
import argparse
import requests
import time

def transcribe_audio(audio_file, output_file=None, api_key=None):
    """
    Transcribe audio file using Groq Whisper API
    
    Args:
        audio_file: Path to audio file
        output_file: Output subtitle file path (optional)
        api_key: Groq API key (optional, can use GROQ_API_KEY env var)
    
    Returns:
        str: Transcribed text
    """
    
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        return None
    
    # Get API key from argument or environment
    if not api_key:
        api_key = os.environ.get('GROQ_API_KEY')
    
    if not api_key:
        print("❌ 未找到 Groq API Key")
        print("   请设置环境变量: export GROQ_API_KEY='your-api-key'")
        print("   或使用参数: --api-key YOUR_KEY")
        return None
    
    file_size = os.path.getsize(audio_file) / (1024 * 1024)
    print(f"🎤 开始转录音频...")
    print(f"   文件: {audio_file} ({file_size:.1f} MB)")
    
    # Check file size (Groq has 25MB limit)
    if file_size > 25:
        print(f"⚠️  警告: 文件大小 {file_size:.1f} MB 超过 Groq 限制 (25 MB)")
        print("   建议压缩音频或分段处理")
        return None
    
    # Prepare API request
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        with open(audio_file, 'rb') as f:
            files = {
                'file': (os.path.basename(audio_file), f, 'audio/mpeg')
            }
            data = {
                'model': 'whisper-large-v3',
                'response_format': 'verbose_json',
                'temperature': 0
            }
            
            print("   正在调用 Groq Whisper API...")
            start_time = time.time()
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
            elapsed = time.time() - start_time
            print(f"   API 响应时间: {elapsed:.1f} 秒")
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '')
                
                if not text:
                    print("❌ 转录结果为空")
                    return None
                
                word_count = len(text)
                print(f"✅ 转录成功!")
                print(f"   字符数: {word_count:,}")
                print()
                
                # Save to file if specified
                if output_file:
                    with open(output_file, 'w', encoding='utf-8') as out:
                        out.write(text)
                    print(f"📝 转录文本已保存到: {output_file}")
                
                return text
                
            else:
                print(f"❌ API 请求失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ 转录失败: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Transcribe audio using Groq Whisper API')
    parser.add_argument('audio_file', help='Path to audio file')
    parser.add_argument('--output', help='Output text file path (optional)')
    parser.add_argument('--api-key', help='Groq API key (optional, uses GROQ_API_KEY env var)')
    
    args = parser.parse_args()
    
    text = transcribe_audio(args.audio_file, args.output, args.api_key)
    
    if text:
        print()
        print("=" * 60)
        print("转录文本:")
        print("=" * 60)
        print(text)
        print("=" * 60)
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
