---
name: sva
description: Agent-centric video analysis (YouTube/MP4) using local files and HTML viewer with AI chat. Processes transcripts, creates chapters, generates summaries, and enables contextual chat with video content. Use for step-by-step analysis of long videos using free AI models.
author: Piotr Ratajski
website: https://ratajskipiotr.pl/
license: MIT
---

# Simple Video Analyzer Skill

Comprehensive guide for analyzing video content without a persistent backend server. This skill is designed for direct agent interaction, focusing on local file processing, standalone HTML viewer, and integrated AI chat functionality.

**Author:** Piotr Ratajski - https://ratajskipiotr.pl/

## When to Apply

Reference these guidelines when:
*   A user provides a video URL (YouTube or direct MP4 link).
*   The goal is to extract transcripts, create video chapters, or generate summaries.
*   There's a need for a serverless, agent-driven analysis workflow.
*   The user prefers local file processing and a simple HTML interface over a running server.
*   User wants to chat with AI about video content using transcript as context.
*   User wants to avoid burning tokens on paid plans by using free AI models.

## Core Components by Priority

| Priority | Component | Impact | Description |
| ------- | -------- | -------- | ----------- |
| 1 | `SKILL.md` | CRITICAL | High-level instructions, workflow, and meta-information for the agent. Defines how to use the skill. |
| 2 | `assets/template.html` | CRITICAL | The standalone HTML viewer for presenting video, chapters, and analysis results (without chat). |
| 3 | `analysis/session_X/viewer_with_chat.html` | HIGH | HTML viewer with integrated AI chat functionality. Supports multiple AI models and contextual conversations. |
| 4 | `scripts/example_script.cjs` | LOW | Placeholder script file. Actual VTT parsing is done via Python inline. |

## Workflow Overview

The agent orchestrates the following steps:

1.  **Initiation:**
    *   Ask the user for the video URL.
    *   **Crucially, ask:** "Do you want to download only the transcript, or the video file as well?"
    *   **Crucially, ask:** "Do you have your own API key (e.g., Groq, Mistral) for analysis, or should I delegate this task to another agent (e.g., `opencode, gemini-cli, kilo-cli`)?"
    *   **Optional:** Ask which AI model they prefer, or inform that the system will automatically select the "biggest/best" available model.

2.  **API Model Discovery & Testing (Agent Responsibility):**
    *   **Agent reads API key:** From `api.txt` file or provided by user.
    *   **Query available models:** Use API endpoint (e.g., `https://api.mistral.ai/v1/models` for Mistral).
    *   **Select "best" model:** Based on: name containing 'large', 'latest', or having the largest context window. For Mistral, typically `mistral-large-latest` or similar.
    *   **Test the model:** Send a simple test query (e.g., "Test: answer briefly 'OK'") to verify the model works and returns a response.
    *   **Save model information:** In session directory as `models.json`.
    *   **Configure HTML:** Agent injects API key and selected model directly into the HTML file (no UI for user to enter these).
    *   **If test fails:** Report error to user and suggest checking API key or trying a different model.

3.  **Downloading & Processing:**
    *   Use `yt-dlp` (via shell command) based on the user's choice for transcript-only or video+transcript.
        *   Transcript-only: `yt-dlp --write-auto-subs --skip-download --output "%(title)s" URL`
        *   Video + Subs: `yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" --write-auto-subs --output "%(title)s" URL`
        *   **Important:** Using `%(title)s` in the output template ensures the video file is named after the video title.
    *   Parse the downloaded subtitle file (`.vtt` or `.srt`) into a JSON array of `[timestamp, text]` pairs using Python inline code. The parsing should:
        *   Extract timestamps and text from VTT/SRT format
        *   Clean HTML tags and duplicate entries
        *   Output a clean JSON array saved as `transcript_clean.json`
    *   **Prepare clean transcript:** Create a `clean_transcript.txt` file containing ONLY the text without timestamps, HTML tags, or any markup. This is used for AI context to avoid token waste.

4.  **Chapter & Summary Generation:**
    *   **If user provided API key:** Use the key to call an AI model (e.g., Mistral) with the transcript to generate chapter titles and summaries.
        *   Send the cleaned transcript text to the API (use `clean_transcript.txt` to avoid token waste)
        *   **Crucially: Include user's awareness level and goals in the prompt.** Ask the user about their:
            - Knowledge level (beginner, intermediate, expert)
            - Specific learning objectives or what they want to achieve
            - Any particular aspects of the video they're most interested in
        *   Request a JSON structure with 5-8 chapters, each having: start time, title, and summary **tailored to user's expertise and goals**
        *   Use the first timestamp from transcript for each chapter
        *   **Prompt engineering tip:** Structure the API call like:
            ```
            System: You are analyzing a video transcript for a user with [level] knowledge who wants to [goal].
            Focus on [specific interests]. Provide chapter summaries that are [technical/simple/actionable].
            Transcript: [clean_transcript.txt content]
            ```
    *   **If delegating:** Use agent invocation (e.g., `generalist`) with the transcript and instructions to return a JSON structure for chapters and their summaries. Include user context.
    *   Structure the output into a JSON object suitable for `assets/template.html`.

5.  **Visualization:**
    *   Create a session-specific directory (e.g., `analysis/[session_id]/`).
    *   Save the following files in the session directory:
        *   `data.json` - Contains title, video path, chapters with summaries
        *   `models.json` - Contains available models and default model selection
        *   `clean_transcript.txt` - Clean transcript text without timestamps or markup (for AI context)
        *   `transcript_clean.json` - Transcript with timestamps in JSON format
        *   Video file (titled) - Copy/move the video file here for proper relative path access
        *   Subtitle files (`.vtt`) - Copy transcript files to the session folder
        *   `viewer.html` - Basic HTML viewer (video + chapters, no chat)
        *   `viewer_with_chat.html` - **Enhanced HTML viewer with integrated AI chat functionality (API pre-configured by agent)**
    *   **Chat-enabled HTML (`viewer_with_chat.html`) features:**
        *   Two-panel layout: left (video + chapters), right (chat interface)
        *   **NO API configuration UI** - API key and model are pre-configured by the agent in the HTML source
        *   Status display showing configured API and model (read-only)
        *   Chat interface with:
            - Message history display (user messages on right, AI on left)
            - Text input area with Enter to send (Shift+Enter for new line)
            - Chat context includes: chapter list with timestamps, full clean transcript
            - Chat history persisted in browser localStorage, preserved between page reloads
        *   Video and chapters in left panel with click-to-seek functionality
        *   **Agent responsibilities for HTML configuration:**
            - Inject API key into JavaScript constant `API_KEY`
            - Inject selected model into JavaScript constant `MODEL`
            - Set API endpoint in `API_ENDPOINT` constant
            - Test the model before finalizing HTML to ensure it works
    *   Provide the user with instructions to open `viewer_with_chat.html` for full functionality.

## How to Use

1.  **Agent Action:** When a request involves analyzing a video, the agent should:
    *   Ask the user the clarifying questions defined in the **Initiation** step.
    *   Execute `yt-dlp` using shell command with title-based output naming.
    *   Parse subtitles using Python inline code (handle VTT/SRT formats).
    *   Prepare clean transcript (`clean_transcript.txt`) without timestamps or markup.
    *   **Configure API (Agent Responsibility):**
        *   Read API key from `api.txt` or provided by user.
        *   Discover available models from the API endpoint.
        *   Select the "best" model (largest/latest) - if user specified a model, use that; otherwise auto-select.
        *   Test the model with a simple query to verify it works.
        *   Generate chapters and summaries using the API.
    *   **If delegating:** Use agent invocation (e.g., `generalist`) for chapter generation.
    *   Create session directory with all related files:
        *   Video file (titled), subtitle files, `clean_transcript.txt`, `transcript_clean.json`
        *   `data.json`, `models.json`
        *   `viewer.html` (basic), `viewer_with_chat.html` (with AI chat)
    *   **Inject API configuration into HTML:** In `viewer_with_chat.html`:
        *   Set `API_KEY` constant with the API key
        *   Set `MODEL` constant with the selected model
        *   Set `API_ENDPOINT` constant with the correct endpoint
        *   NO API configuration UI for the user - everything is pre-configured
    *   Instruct the user to open `viewer_with_chat.html` for full functionality.

2.  **User Action:**
    *   The user opens the `viewer_with_chat.html` file from the session directory in their browser.
    *   **No API configuration needed** - agent already configured everything.
    *   Status display shows: "API Configured: [Provider] | Model: [Model Name]"
    *   Can immediately chat with AI about the video content - the AI has full context of:
        *   Chapter list with timestamps and summaries
        *   Full clean transcript
    *   Left panel shows video and chapters - clicking seeks to timestamp.

## Additional Context

*   **VTT Parsing:** Since `scripts/process.py` doesn't exist, the agent should parse VTT files inline using Python. The parsing should handle:
    *   WEBVTT headers and metadata
    *   Timestamp lines (00:00:00.000 --> 00:00:02.000)
    *   HTML tags within text (like `<c>`, `<00:00:00.480>`)
    *   Duplicate text entries from overlapping timestamps
    *   Output: `transcript_clean.json` (with timestamps) and `clean_transcript.txt` (text only)
*   **Clean Transcript:** The `clean_transcript.txt` file should contain ONLY the transcript text without:
    *   Timestamps
    *   HTML tags or markup
    *   Any formatting
    *   This is used as context for AI chat to avoid wasting tokens on non-content text.
*   **`assets/template.html`:** This is a static HTML file for basic viewing. The agent should:
    *   Inject the processed data directly into the `<script>` tag within a new HTML file
    *   Save this new file as `viewer.html` in the session directory
    *   Ensure the video path is relative and points to the video file in the same directory
*   **HTML with Chat (`viewer_with_chat.html`):**
    *   Two-panel layout: left (video + chapters), right (chat interface)
    *   **NO API Configuration UI** - Agent pre-configures everything in JavaScript constants
    *   Status display showing: "API Configured: [Provider] | Model: [Model]"
    *   Chat interface:
        *   Message display with user/AI distinction
        *   Text input with Enter to send (Shift+Enter for new line)
        *   Chat context automatically includes: chapter list + clean transcript
    *   Video player with chapters that seek on click
    *   **Agent sets in HTML source (not visible to user as form fields):**
        *   `API_KEY` - The API key (from api.txt or user)
        *   `MODEL` - Selected "best" model or user-specified model
        *   `API_ENDPOINT` - Correct endpoint for the API provider
*   **`yt-dlp`:** Ensure `yt-dlp` is available in the environment where the agent runs, or provide instructions on how to install it.
    *   If not available, download it directly: `python3 -c "import urllib.request; urllib.request.urlretrieve('https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp', 'yt-dlp')"`
*   **Session Directory Structure:**
    1. **Create session folder** before starting: `analysis/session_X/` (where `X` is session number, e.g., `session_1`).
    2. **All files** (video, transcript, HTML, JSON) **must** be saved in this folder.
    Example structure:
    ```
    analysis/
    └── session_1/
        ├── video_title.mp4          # Video file (name = video title)
        ├── video_title.en.vtt       # Transcript (auto-downloaded)
        ├── transcript_clean.json    # Transcript with timestamps (JSON)
        ├── clean_transcript.txt     # Clean text (no timestamps, HTML tags)
        ├── data.json                # Data: title, video path, chapters
        ├── models.json              # Available AI models and selected model
        ├── viewer.html              # Basic view (video + chapters)
        └── viewer_with_chat.html     # View with AI chat (preconfigured)
    ```
    **Note:** Agent **must** create the session folder **before** downloading files and processing.
*   **API Integration (Agent Responsibility):** When using Mistral API:
    *   **Read API key:** From `api.txt` file (format: `mistralapi="key"`) or provided by user.
    *   **Model Discovery:**
        *   Endpoint: `https://api.mistral.ai/v1/models`
        *   Fetch available models and identify "best" model (contains 'large', 'latest', or has largest context)
        *   If user specified a model, use that; otherwise auto-select "best"
        *   Save model list as `models.json`
    *   **Model Testing:**
        *   Send test query: "Test: answer briefly 'OK'"
        *   Verify response is received before finalizing HTML
    *   **HTML Configuration (Agent injects these constants):**
        *   `API_KEY` - The API key
        *   `MODEL` - Selected model (user-specified or auto-selected "best")
        *   `API_ENDPOINT` - Chat endpoint: `https://api.mistral.ai/v1/chat/completions`
    *   **Chat Context:** System message includes:
        *   Chapter list with timestamps and summaries
        *   Full clean transcript (first 15000 chars to avoid token limits)
        *   Last 20 messages from chat history (persisted in localStorage, sent to AI with each request)
        *   **User context (CRITICAL):** User's awareness level (beginner/intermediate/expert) and goals for watching the video
        *   **Important instruction to AI:** "Answer in plain text, without markdown formatting (bold, lists, tables). Use only simple newline characters (\n) for formatting. Do not use: **, *, _, `, or tables. Write in natural text."
        *   **Tailor responses to user's expertise:** If user is a beginner, explain concepts simply. If expert, provide technical details and skip basics. Always focus on what the user wants to achieve."
    *   **Chat Parameters:**
        *   Model: `MODEL` constant from HTML
        *   Temperature: 0.7 for chat (more creative)
        *   Max tokens: appropriate for response length
    *   **User sees:** Status display "API Configured: [Provider] | Model: [Model]" - no configuration needed.
*   **Default Model Selection Logic:**
    *   Priority 1: Model name contains 'large' (e.g., 'mistral-large-latest')
    *   Priority 2: Model name contains 'latest' (e.g., 'mistral-medium-latest')
    *   Priority 3: First model in the list
    *   Example: For Mistral API, `mistral-large-2512` or `mistral-large-latest` would be selected as default.

This structure emphasizes clarity, agent autonomy, and user-friendliness by leveraging local files and a simple HTML viewer.

## Author

**Piotr Ratajski**  
https://ratajskipiotr.pl/
