---
name: youtube-subtitle-summary
description: >
  Download subtitles from YouTube videos and generate AI-powered content summaries.
  If subtitles are not available, automatically download video, extract audio, transcribe using Groq Whisper API, and generate summary.
  Use when the user needs to: (1) Download subtitles from a YouTube video URL,
  (2) Summarize YouTube video content without watching the full video,
  (3) Extract and analyze transcript text from YouTube videos,
  (4) Get quick insights from long YouTube videos,
  (5) Transcribe videos without subtitles.
  Keywords: YouTube, subtitle, transcript, summary, video analysis, content extraction, Whisper, transcription.
---

# YouTube Subtitle Summary

Download subtitles from YouTube videos and generate AI-powered summaries. If subtitles are unavailable, automatically transcribe audio using Groq Whisper API.

## Prerequisites

### Install Deno JavaScript Runtime

YouTube's n-parameter challenge requires a JavaScript engine. Install Deno:

```bash
# Install unzip (required for Deno installation)
apt-get install -y unzip

# Install Deno
curl -fsSL https://deno.land/install.sh | sh
```

**Deno installation location**: `/root/.deno/bin/deno`

**Add to PATH**:
```bash
export PATH="/root/.deno/bin:$PATH"
```

**Why Deno?**
- YouTube uses JavaScript-based challenges to prevent bot downloads
- yt-dlp requires a JavaScript runtime to solve these challenges
- Deno is lightweight and easy to install

## Workflow

### Step 1: Download Subtitles

Use the `download_subtitle.py` script to download subtitles from a YouTube video:

```bash
python3 scripts/download_subtitle.py <youtube_url> [--lang LANG] [--output OUTPUT_DIR]
```

**Parameters:**
- `youtube_url`: YouTube video URL (required)
- `--lang`: Subtitle language codes, comma-separated (default: `zh,en`)
- `--output`: Output directory for subtitle files (default: current directory)

**Example:**
```bash
python3 scripts/download_subtitle.py "https://www.youtube.com/watch?v=VIDEO_ID" --lang zh --output ./subtitles
```

### Step 2: If No Subtitles Available

When subtitles are not available, follow these steps:

#### 2.1 Download Video

Download the **lowest resolution** video to minimize file size.

**Method 1: Android Client + Deno (No cookies needed)**

For most public videos:

```bash
export PATH="/root/.deno/bin:$PATH"
yt-dlp --js-runtimes deno \
  --remote-components ejs:github \
  --extractor-args "youtube:player_client=android" \
  -f "worst" \
  -o "%(id)s.%(ext)s" \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Method 2: Android Client + Cookies + Deno (Most powerful)**

For protected videos or when Method 1 fails:

```bash
export PATH="/root/.deno/bin:$PATH"
yt-dlp --cookies cookies.txt \
  --js-runtimes deno \
  --remote-components ejs:github \
  --extractor-args "youtube:player_client=android" \
  -f "worst" \
  -o "%(id)s.%(ext)s" \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Parameter Explanation:**

- `--js-runtimes deno`: Use Deno to solve YouTube's JavaScript challenges (required)
- `--remote-components ejs:github`: Download remote components from GitHub (required)
- `--extractor-args "youtube:player_client=android"`: Use Android client API to bypass desktop restrictions
- `-f "worst"`: Download lowest resolution to minimize file size (typically 10-30 MB for 10-20 min videos)
- `-o "%(id)s.%(ext)s"`: Output filename format (e.g., `lR7GaZYdsAg.mp4`)
- `--cookies cookies.txt`: Use browser cookies for authentication (Method 2 only)

**When to use which method:**

- **Method 1**: Try this first for public videos (no cookies needed)
- **Method 2**: Use when Method 1 fails or video requires authentication

**Important**:
- Deno is **always required** for YouTube downloads (JavaScript challenges)
- Always use `worst` format to keep audio file size under 25MB (Groq API limit)
- Typical file size: 10-30 MB for 10-20 minute videos
- If file is still too large, consider downloading shorter segments

#### 2.2 Extract Audio

Use `extract_audio.py` to extract audio from video:

```bash
python3 scripts/extract_audio.py <video_file> [--output OUTPUT_FILE]
```

**Example:**
```bash
python3 scripts/extract_audio.py video.webm --output audio.mp3
```

**Output**: MP3 audio file (128kbps, 44.1kHz)

#### 2.3 Transcribe Audio

Use `transcribe_audio.py` with Groq Whisper API:

```bash
export GROQ_API_KEY='your-groq-api-key'
python3 scripts/transcribe_audio.py <audio_file> [--output OUTPUT_FILE]
```

**Example:**
```bash
python3 scripts/transcribe_audio.py audio.mp3 --output transcript.txt
```

**Requirements:**
- Groq API key (set via `GROQ_API_KEY` environment variable or `--api-key` parameter)
- Audio file must be < 25 MB (Groq limit)
- Supported formats: MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM

**Get Groq API Key**: https://console.groq.com/keys

### Step 3: Analyze and Summarize

After obtaining transcript (from subtitles or Whisper), use AI to generate a **detailed summary** that restores the original video content.

## Success Cases

### Case 1: Public Video (Rick Astley - Never Gonna Give You Up)
```bash
# Video ID: dQw4w9WgXcQ
# Method: Android client + Deno (no cookies)
export PATH="/root/.deno/bin:$PATH"
yt-dlp --js-runtimes deno --remote-components ejs:github \
  --extractor-args "youtube:player_client=android" \
  -f "worst" -o "%(id)s.%(ext)s" \
  "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Result: 11.28 MB video → 3.3 MB audio → 3.6 KB summary
```

### Case 2: Protected Video (沙县小吃探访)
```bash
# Video ID: FOSgHdeDAcw
# Method: Cookies + Deno + Android client
export PATH="/root/.deno/bin:$PATH"
yt-dlp --cookies cookies.txt --js-runtimes deno \
  --remote-components ejs:github \
  --extractor-args "youtube:player_client=android" \
  -f "worst" -o "%(id)s.%(ext)s" \
  "https://www.youtube.com/watch?v=FOSgHdeDAcw"

# Result: 18.19 MB video → 13.0 MB audio → 8.8 KB summary
# Transcription: 4.0 seconds, 2,943 characters
```

### Case 3: Long Analysis Video (新世界秩序分析)
```bash
# Video ID: lR7GaZYdsAg
# Method: Cookies + Deno + Android client
export PATH="/root/.deno/bin:$PATH"
yt-dlp --cookies cookies.txt --js-runtimes deno \
  --remote-components ejs:github \
  --extractor-args "youtube:player_client=android" \
  -f "worst" -o "%(id)s.%(ext)s" \
  "https://www.youtube.com/watch?v=lR7GaZYdsAg"

# Result: 25.40 MB video → 22.9 MB audio → 15 KB summary
# Transcription: 7.9 seconds, 7,929 characters
# Duration: ~20 minutes
```

**Key Takeaways:**
- **Deno is always required** for YouTube downloads (JavaScript challenges)
- Lowest resolution keeps files manageable (10-30 MB)
- Audio extraction is fast and efficient
- Groq Whisper transcription is very fast (3-8 seconds)
- Detailed summaries capture full video content (3-15 KB)
- Space saved per video: 15-50 MB after cleanup

### Step 3: Analyze and Summarize (continued)

After obtaining transcript (from subtitles or Whisper), use AI to generate a **detailed summary** that restores the original video content.

**Important Requirements:**
- **Be detailed**: The summary should be comprehensive enough to understand the video without watching it
- **Restore content**: Include all major points, arguments, and details from the original
- **Save to file**: Always save the summary as a markdown file (e.g., `summary_<video_id>.md`)
- **Display to user**: Show the complete summary to the user after generation

**Detailed Summary Format:**

```markdown
# YouTube 视频详细总结

**视频ID**: [Video ID]
**标题**: [Video Title]
**时长**: [Duration]
**转录来源**: [字幕 / Groq Whisper API]
**生成时间**: [YYYY-MM-DD HH:MM]

---

## 📊 视频概述

[2-3 paragraphs providing context, background, and overall theme of the video]

---

## 🎯 详细内容分析

### [Section 1 Title]
[Detailed description of this section, including:
- Main points discussed
- Key arguments or statements
- Important details or examples
- Quotes or specific data mentioned]

### [Section 2 Title]
[Continue with detailed analysis of each major section...]

### [Section 3 Title]
[...]

---

## 💡 主题与意义

### 1. [Theme 1]
[Explain the deeper meaning or significance]

### 2. [Theme 2]
[...]

### 3. [Theme 3]
[...]

---

## 📝 总结

[2-3 paragraphs summarizing the key takeaways and overall message. This should capture the essence of the video in a way that someone who hasn't watched it can understand the main points.]

---

## 🔑 关键词

[List of relevant keywords for searchability]

---

**注**: 本总结基于 [字幕/Whisper转录] 生成，力求还原视频的完整内容和核心观点。
```

**Summary Guidelines:**

1. **Comprehensive Coverage**: Include all major topics, arguments, and details
2. **Logical Structure**: Organize content by themes or chronological order
3. **Preserve Details**: Don't oversimplify - include specific examples, data, quotes
4. **Context**: Provide background information to help readers understand
5. **Depth**: Each section should have multiple paragraphs, not just bullet points
6. **Accuracy**: Stay faithful to the original content, don't add interpretations
7. **Readability**: Use clear headings, formatting, and structure

### Step 4: Save Summary and Cleanup

After generating the detailed summary:

1. **⚠️ CRITICAL: Generate meaningful filename (MANDATORY)**:
   ```bash
   # Summary filename MUST reflect the video content
   # Format: summary_<video_id>_<descriptive_title>.md
   # Example: summary_lR7GaZYdsAg_新世界秩序分析.md
   # Example: summary_RbEpEKnJvok_Claude_Skills七天实战营第一课.md
   # 
   # ❌ WRONG: summary_<video_id>.md (too generic, not descriptive)
   # ✅ CORRECT: summary_<video_id>_<clear_chinese_title>.md
   ```

   **Filename Requirements:**
   - MUST include video ID for traceability
   - MUST include descriptive Chinese title (10-30 characters)
   - Title should clearly indicate video topic/content
   - Use underscores (_) to separate parts
   - Remove special characters that may cause file system issues
   - Keep filename under 100 characters total

2. **Save summary to file**:
   - The summary markdown file should have a descriptive title in the first heading
   - Include video ID, title, duration, and source in the metadata
   - Filename example: `summary_dQw4w9WgXcQ_Rick_Astley经典MV.md`

3. **Display summary to user**: Show the complete summary content

4. **Cleanup temporary files** to save disk space:
   ```bash
   rm video_file.mp4 audio_file.mp3 transcript.txt
   ```

**Important**: 
- ✅ **Keep**: Summary markdown file (summary_<video_id>_<descriptive_title>.md) with meaningful title
- ❌ **Delete**: Video file, audio file, transcript text file
- 💾 **Space saved**: Typically 10-50 MB per video
- 📝 **Filename**: ALWAYS use descriptive titles that reflect video content (NOT just video_id)

**File organization**:
```
youtube-summaries/
├── summary_VIDEO_ID_1_描述性标题.md  ← Keep (descriptive filename)
├── summary_VIDEO_ID_2_描述性标题.md  ← Keep (descriptive filename)
└── cookies.txt                      ← Keep (if needed)

Example:
├── summary_RbEpEKnJvok_Claude_Skills七天实战营第一课.md
├── summary_lR7GaZYdsAg_新世界秩序分析.md
└── cookies.txt
```

## Complete Workflow Example

```bash
# Set working directory
cd /root/.openclaw/workspace/youtube-summaries

# Try to download subtitles first
python3 ../skills/youtube-subtitle-summary/scripts/download_subtitle.py \
  "https://www.youtube.com/watch?v=VIDEO_ID" --lang zh --output .

# If no subtitles, download video (always use Deno)
export PATH="/root/.deno/bin:$PATH"

# Method 1: Try without cookies first
yt-dlp --js-runtimes deno --remote-components ejs:github \
  --extractor-args "youtube:player_client=android" \
  -f "worst" \
  -o "%(id)s.%(ext)s" "https://www.youtube.com/watch?v=VIDEO_ID"

# Method 2: If Method 1 fails, use cookies
yt-dlp --cookies cookies.txt --js-runtimes deno \
  --remote-components ejs:github \
  --extractor-args "youtube:player_client=android" \
  -f "worst" \
  -o "%(id)s.%(ext)s" "https://www.youtube.com/watch?v=VIDEO_ID"

# Extract audio
python3 ../skills/youtube-subtitle-summary/scripts/extract_audio.py VIDEO_ID.mp4

# Transcribe with Whisper
export GROQ_API_KEY='your-api-key'
python3 ../skills/youtube-subtitle-summary/scripts/transcribe_audio.py VIDEO_ID.mp3 --output transcript.txt

# AI generates detailed summary with meaningful title
# ⚠️ CRITICAL: Save to descriptive filename (MANDATORY)
# Format: summary_<video_id>_<descriptive_title>.md
# Example: summary_lR7GaZYdsAg_新世界秩序的形成.md
# NOT: summary_lR7GaZYdsAg.md (too generic!)

# Display summary to user
cat summary_VIDEO_ID_描述性标题.md

# Cleanup temporary files (keep only the summary)
rm VIDEO_ID.mp4 VIDEO_ID.mp3 transcript.txt

# Final result: Only summary_VIDEO_ID_描述性标题.md remains (3-15 KB)
```

## Error Handling

**No subtitles available:**
- Automatically fall back to video download + Whisper transcription
- Ensure Groq API key is set

**Video download fails:**
- Verify YouTube URL is correct
- Check cookies.txt file exists
- Ensure Deno runtime is installed

**Audio file too large (>25MB):**
- Download lower quality video (480p or 360p)
- Split long videos into segments
- Compress audio file

**Groq API errors:**
- Check API key is valid
- Verify API quota/limits
- Check network connection

**Transcription quality issues:**
- Whisper works best with clear audio
- Background noise may affect accuracy
- Consider manual review for critical content

## Tips

- **Prefer subtitles**: Subtitles are faster and more accurate than transcription
- **Video quality**: Use `worst` format to download lowest resolution and keep audio files under 25MB
- **Deno runtime**: Required for YouTube downloads, install once and add to PATH
- **Long videos**: Consider splitting into segments for better processing
- **API costs**: Groq Whisper API is free tier friendly but has rate limits
- **Cleanup**: Always delete temporary files after summarization
- **Meaningful titles**: Summary files should have descriptive titles that reflect video content
- **Android client**: Use `player_client=android` parameter for better download compatibility

## Output Files

- `<video_id>.zh.srt` - Chinese subtitles (if available)
- `<video_id>.en.srt` - English subtitles (if available)
- `<video_id>.webm` - Downloaded video (temporary)
- `<video_id>.mp3` - Extracted audio (temporary)
- `transcript.txt` - Whisper transcription (temporary)

**Remember**: Delete temporary files after summarization!
