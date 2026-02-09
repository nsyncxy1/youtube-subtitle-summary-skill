#!/usr/bin/env python3
"""
Summarize subtitle content using AI
Usage: python3 summarize_subtitle.py <subtitle_file> [--output OUTPUT_FILE]
"""

import sys
import os
import argparse
import re

def parse_srt(srt_file):
    """Parse SRT subtitle file and extract text content"""
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract subtitle text (skip timestamps and sequence numbers)
    lines = content.split('\n')
    text_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip empty lines, sequence numbers, and timestamps
        if not line or line.isdigit() or '-->' in line:
            continue
        text_lines.append(line)
    
    return '\n'.join(text_lines)

def format_time(seconds):
    """Convert seconds to HH:MM:SS or MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def main():
    parser = argparse.ArgumentParser(description='Summarize YouTube subtitle content')
    parser.add_argument('subtitle_file', help='Path to SRT subtitle file')
    parser.add_argument('--output', help='Output file for summary (optional)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.subtitle_file):
        print(f"❌ 字幕文件不存在: {args.subtitle_file}")
        sys.exit(1)
    
    print(f"📖 读取字幕文件: {args.subtitle_file}")
    
    # Parse subtitle content
    subtitle_text = parse_srt(args.subtitle_file)
    
    # Get file info
    file_size = os.path.getsize(args.subtitle_file) / 1024
    word_count = len(subtitle_text)
    line_count = len(subtitle_text.split('\n'))
    
    print(f"   文件大小: {file_size:.1f} KB")
    print(f"   字符数: {word_count:,}")
    print(f"   行数: {line_count:,}")
    print()
    
    # Output subtitle text for AI to analyze
    print("=" * 60)
    print("字幕内容 (供 AI 分析):")
    print("=" * 60)
    print(subtitle_text)
    print("=" * 60)
    print()
    print("✅ 字幕内容已输出，请 AI 进行总结分析")
    
    # Save to file if specified
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(subtitle_text)
        print(f"📝 字幕文本已保存到: {args.output}")
    
    return subtitle_text

if __name__ == '__main__':
    main()
