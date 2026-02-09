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

## 🤖 For AI Assistants: Auto-Setup Required Files

**BEFORE starting any workflow, check if required files exist. If not, ask the user and create them:**

### Check and Create cookies.txt
```bash
# Check if cookies.txt exists
if [ ! -f cookies.txt ]; then
  echo "⚠️ cookies.txt not found. Please provide your YouTube cookies."
fi
```

**If cookies.txt doesn't exist:**
1. Ask user: "请提供你的 YouTube cookies（可以使用浏览器扩展 'Get cookies.txt LOCALLY' 导出）"
2. When user provides cookies content, create the file:
   ```bash
   cat > cookies.txt << 'EOF'
   [user's cookies content]
   EOF
   ```

### Check and Create groq.txt
```bash
# Check if groq.txt exists
if [ ! -f groq.txt ]; then
  echo "⚠️ groq.txt not found. Please provide your Groq API key."
fi
```

**If groq.txt doesn't exist:**
1. Ask user: "请提供你的 Groq API key（可以从 https://console.groq.com/keys 获取）"
2. When user provides the API key, create the file:
   ```bash
   echo "user-provided-api-key" > groq.txt
   ```

**Important:**
- **Always check for these files at the start of the workflow**
- **Create them immediately when user provides the content**
- **Do not proceed without these files** (cookies.txt for most videos, groq.txt for transcription)
- Files should be created in the working directory (e.g., `/root/.openclaw/workspace/youtube-summaries/`)

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

**⚠️ Important: Cookies Auto-Detection**
- The script will **automatically check for `cookies.txt`** in the working directory
- If `cookies.txt` exists, it will be used automatically (no need to specify `--cookies`)
- This applies to both subtitle download and video download steps
- **Recommended**: Always keep `cookies.txt` in your working directory (e.g., `youtube-summaries/cookies.txt`)

### Step 2: If No Subtitles Available

When subtitles are not available, follow these steps:

#### 2.1 Download Video

Download the **lowest resolution** video to minimize file size.

**⚠️ Cookies Auto-Detection (Recommended)**

**Always work in a directory with `cookies.txt` present** (e.g., `youtube-summaries/cookies.txt`). The commands below will automatically use it if available.

**Method 1: Try without explicit --cookies flag first**

For most videos (cookies.txt will be auto-detected if present):

```bash
export PATH="/root/.deno/bin:$PATH"
yt-dlp --js-runtimes deno \
  --remote-components ejs:github \
  --extractor-args "youtube:player_client=android" \
  -f "worst" \
  -o "%(id)s.%(ext)s" \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Method 2: Explicit --cookies flag (when auto-detection fails)**

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
- `--cookies cookies.txt`: Explicitly specify cookies file (usually auto-detected)

**Cookies Behavior:**
- **Auto-detection**: yt-dlp automatically looks for `cookies.txt` in the working directory
- **Explicit flag**: Use `--cookies cookies.txt` only when auto-detection fails
- **Recommended setup**: Keep `cookies.txt` in your working directory (e.g., `youtube-summaries/cookies.txt`)

**When to use which method:**

- **Method 1**: Try this first (cookies auto-detected if present)
- **Method 2**: Use explicit `--cookies` flag when Method 1 fails

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

**🤖 For AI Assistants:**
When the user provides a Groq API key, automatically save it to `groq.txt` in the working directory:
```bash
echo "user-provided-key" > groq.txt
```

**Manual Usage:**
```bash
# Method 1: Save API key to groq.txt (recommended)
echo "your-groq-api-key" > groq.txt
python3 scripts/transcribe_audio.py <audio_file> [--output OUTPUT_FILE]

# Method 2: Use environment variable
export GROQ_API_KEY='your-groq-api-key'
python3 scripts/transcribe_audio.py <audio_file> [--output OUTPUT_FILE]

# Method 3: Pass as parameter
python3 scripts/transcribe_audio.py <audio_file> --api-key your-groq-api-key
```

**Example:**
```bash
# Save API key to groq.txt first
echo "gsk_xxxxxxxxxxxxx" > groq.txt

# Then transcribe
python3 scripts/transcribe_audio.py audio.mp3 --output transcript.txt
```

**Requirements:**
- Groq API key (save to `groq.txt` file, or use `GROQ_API_KEY` environment variable, or `--api-key` parameter)
- Audio file must be < 25 MB (Groq limit)
- Supported formats: MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM

**Get Groq API Key**: https://console.groq.com/keys

**API Key Priority:**
1. `--api-key` parameter (highest priority)
2. `groq.txt` file in current directory (recommended)
3. `GROQ_API_KEY` environment variable (fallback)

### Step 3: Analyze and Summarize

After obtaining transcript (from subtitles or Whisper), use AI to generate a **detailed summary** that restores the original video content.




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
# Set working directory (ensure cookies.txt is present here)
cd /root/.openclaw/workspace/youtube-summaries

# ⚠️ IMPORTANT: Ensure cookies.txt exists in this directory
# yt-dlp will automatically detect and use it

# Try to download subtitles first (cookies auto-detected)
python3 ../skills/youtube-subtitle-summary/scripts/download_subtitle.py \
  "https://www.youtube.com/watch?v=VIDEO_ID" --lang zh --output .

# If no subtitles, download video (always use Deno)
export PATH="/root/.deno/bin:$PATH"

# Method 1: Try without explicit --cookies flag (auto-detection)
yt-dlp --js-runtimes deno --remote-components ejs:github \
  --extractor-args "youtube:player_client=android" \
  -f "worst" \
  -o "%(id)s.%(ext)s" "https://www.youtube.com/watch?v=VIDEO_ID"

# Method 2: If Method 1 fails, use explicit --cookies flag
yt-dlp --cookies cookies.txt --js-runtimes deno \
  --remote-components ejs:github \
  --extractor-args "youtube:player_client=android" \
  -f "worst" \
  -o "%(id)s.%(ext)s" "https://www.youtube.com/watch?v=VIDEO_ID"

# Extract audio
python3 ../skills/youtube-subtitle-summary/scripts/extract_audio.py VIDEO_ID.mp4

# Transcribe with Whisper (groq.txt should be in working directory)
# ⚠️ Ensure groq.txt exists with your API key
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
- **Cookies auto-detection**: Keep `cookies.txt` in working directory (e.g., `youtube-summaries/cookies.txt`), yt-dlp will auto-detect it
- **Groq API key**: Keep `groq.txt` in working directory for automatic API key loading
- **Long videos**: Consider splitting into segments for better processing
- **API costs**: Groq Whisper API is free tier friendly but has rate limits
- **Cleanup**: Always delete temporary files after summarization
- **Meaningful titles**: Summary files should have descriptive titles that reflect video content
- **Android client**: Use `player_client=android` parameter for better download compatibility

## Required Files in Working Directory

For smooth operation, ensure these files exist in your working directory (e.g., `/root/.openclaw/workspace/youtube-summaries/`):

### 1. **`cookies.txt`** (required for most videos)
   - Export from your browser using extensions like "Get cookies.txt LOCALLY"
   - yt-dlp automatically detects and uses it
   - Needed for age-restricted or sign-in required videos

### 2. **`groq.txt`** (required for transcription)
   - Contains your Groq API key (one line)
   - Get API key from: https://console.groq.com/keys
   - Automatically loaded by `transcribe_audio.py`

### 🤖 For AI Assistants: Auto-Create Missing Files

**If files don't exist, ask the user and create them immediately:**

**Missing cookies.txt:**
```bash
# Ask user for cookies content, then create:
cat > cookies.txt << 'EOF'
[paste user's cookies here]
EOF
```

**Missing groq.txt:**
```bash
# Ask user for Groq API key, then create:
echo "user-provided-api-key" > groq.txt
```

**Prompts to use:**
- For cookies: "请提供你的 YouTube cookies（使用浏览器扩展 'Get cookies.txt LOCALLY' 导出）"
- For Groq key: "请提供你的 Groq API key（从 https://console.groq.com/keys 获取）"

**Setup once, use forever:**
```bash
cd /root/.openclaw/workspace/youtube-summaries
# Files will be auto-created when user provides content
# Or manually add:
# - cookies.txt (export from browser)
# - groq.txt (API key from Groq console)
```

## Output Files

- `<video_id>.zh.srt` - Chinese subtitles (if available)
- `<video_id>.en.srt` - English subtitles (if available)
- `<video_id>.webm` - Downloaded video (temporary)
- `<video_id>.mp3` - Extracted audio (temporary)
- `transcript.txt` - Whisper transcription (temporary)

**Remember**: Delete temporary files after summarization!
