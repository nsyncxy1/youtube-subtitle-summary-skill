#!/usr/bin/env python3
"""
Download subtitles from YouTube video
Usage: python3 download_subtitle.py <youtube_url> [--lang LANG] [--output OUTPUT_DIR]
"""

import sys
import os
import argparse
import subprocess
import json

def download_subtitle(youtube_url, lang='zh,en', output_dir='.'):
    """
    Download subtitles from YouTube video using yt-dlp
    
    Args:
        youtube_url: YouTube video URL
        lang: Subtitle language codes (comma-separated, e.g., 'zh,en')
        output_dir: Output directory for subtitle files
    
    Returns:
        dict: Information about downloaded subtitles
    """
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get video info first
    info_cmd = [
        'yt-dlp',
        '--dump-json',
        '--skip-download',
        youtube_url
    ]
    
    try:
        result = subprocess.run(info_cmd, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)
        video_id = video_info.get('id', 'unknown')
        video_title = video_info.get('title', 'Unknown Title')
        duration = video_info.get('duration', 0)
        
        print(f"📹 视频信息:")
        print(f"   标题: {video_title}")
        print(f"   ID: {video_id}")
        print(f"   时长: {duration // 60}:{duration % 60:02d}")
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 获取视频信息失败: {e.stderr}")
        return None
    
    # Download subtitles
    download_cmd = [
        'yt-dlp',
        '--write-sub',
        '--write-auto-sub',
        '--sub-lang', lang,
        '--convert-subs', 'srt',
        '--skip-download',
        '-o', f'{output_dir}/{video_id}.%(ext)s',
        youtube_url
    ]
    
    # Add cookies if available
    cookies_path = os.path.join(output_dir, 'cookies.txt')
    if os.path.exists(cookies_path):
        download_cmd.extend(['--cookies', cookies_path])
    
    # Add Deno runtime if available
    deno_path = '/root/.deno/bin/deno'
    if os.path.exists(deno_path):
        # Set PATH environment variable
        env = os.environ.copy()
        env['PATH'] = f"/root/.deno/bin:{env.get('PATH', '')}"
        
        download_cmd.extend([
            '--js-runtimes', 'deno',
            '--remote-components', 'ejs:github'
        ])
    else:
        env = None
    
    try:
        print("📥 下载字幕中...")
        result = subprocess.run(download_cmd, capture_output=True, text=True, check=True, env=env)
        print(result.stdout)
        
        # Find downloaded subtitle files
        subtitle_files = []
        for file in os.listdir(output_dir):
            if file.startswith(video_id) and file.endswith('.srt'):
                subtitle_files.append(os.path.join(output_dir, file))
        
        if not subtitle_files:
            print("⚠️  未找到字幕文件")
            return None
        
        print(f"✅ 字幕下载成功:")
        for file in subtitle_files:
            file_size = os.path.getsize(file) / 1024
            print(f"   - {os.path.basename(file)} ({file_size:.1f} KB)")
        
        return {
            'video_id': video_id,
            'video_title': video_title,
            'duration': duration,
            'subtitle_files': subtitle_files,
            'output_dir': output_dir
        }
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 下载字幕失败: {e.stderr}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Download YouTube subtitles')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('--lang', default='zh,en', help='Subtitle language codes (default: zh,en)')
    parser.add_argument('--output', default='.', help='Output directory (default: current directory)')
    
    args = parser.parse_args()
    
    result = download_subtitle(args.url, args.lang, args.output)
    
    if result:
        print()
        print("📊 下载完成!")
        print(f"   输出目录: {result['output_dir']}")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
