#!/usr/bin/env python3
"""
Extract audio from video file
Usage: python3 extract_audio.py <video_file> [--output OUTPUT_FILE]
"""

import sys
import os
import argparse
import subprocess

def extract_audio(video_file, output_file=None):
    """
    Extract audio from video file using ffmpeg
    
    Args:
        video_file: Path to video file
        output_file: Output audio file path (optional, defaults to video_name.mp3)
    
    Returns:
        str: Path to extracted audio file
    """
    
    if not os.path.exists(video_file):
        print(f"❌ 视频文件不存在: {video_file}")
        return None
    
    # Generate output filename if not provided
    if not output_file:
        base_name = os.path.splitext(video_file)[0]
        output_file = f"{base_name}.mp3"
    
    print(f"🎵 提取音频中...")
    print(f"   输入: {video_file}")
    print(f"   输出: {output_file}")
    
    # Extract audio using ffmpeg
    cmd = [
        'ffmpeg',
        '-i', video_file,
        '-vn',  # No video
        '-acodec', 'libmp3lame',  # MP3 codec
        '-ab', '128k',  # Bitrate
        '-ar', '44100',  # Sample rate
        '-y',  # Overwrite output file
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / (1024 * 1024)
            print(f"✅ 音频提取成功: {output_file} ({file_size:.1f} MB)")
            return output_file
        else:
            print(f"❌ 音频文件未生成")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 音频提取失败: {e.stderr}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Extract audio from video file')
    parser.add_argument('video_file', help='Path to video file')
    parser.add_argument('--output', help='Output audio file path (optional)')
    
    args = parser.parse_args()
    
    audio_file = extract_audio(args.video_file, args.output)
    
    if audio_file:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
