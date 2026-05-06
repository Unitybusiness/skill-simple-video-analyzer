# Simple Video Analyzer (SVA) Skill

An AI agent skill for step-by-step analysis of long videos.

## Purpose

Analyzing long videos (YouTube/MP4) without a server, with chapter creation and step-by-step analysis. Uses **free AI models** (Groq, Mistral, etc.) to avoid burning tokens on limited paid plans.

## What it does

1. Downloads transcript and optionally the video file (via yt-dlp)
2. Creates chapters based on transcript
3. Generates section summaries
4. Enables contextual AI chat about video content
5. Exports results to a standalone HTML file with built-in chat

## Why use it

- **Token savings** - analyze long videos using free models
- **No server needed** - everything runs locally
- **Step-by-step** - agent guides through the analytical process
- **Multi-model support** - works with Groq, Mistral, and other free APIs

## Installation

### OpenCode
```bash
npx skills add https://github.com/YOUR_USER/skill-simple-video-analyzer --skill sva
```

### Claude Code / Others
```bash
npx skills add https://github.com/YOUR_USER/skill-simple-video-analyzer
```

### Manual
Copy the `sva/` directory to:
- `.opencode/skills/` (project-level)
- `~/.config/opencode/skills/` (global)

## Usage

In OpenCode, type:
```
/sva
```

The agent will ask:
- Video URL (YouTube or MP4)
- Whether to download transcript only or video + transcript
- For an API key for free models (Groq/Mistral) or to delegate to another agent

## Getting the Best Results

For optimal analysis, **clearly state your awareness level and what you want to achieve:**

**Example prompts:**
- *"I'm a beginner in machine learning. Analyze this 2-hour lecture and give me the key concepts I should understand."*
- *"I'm familiar with React basics. Watch this advanced tutorial and extract practical patterns I can apply in my projects."*
- *"I'm researching cloud architecture. This video covers AWS services - I need a technical deep-dive summary focusing on cost optimization strategies."*

**Why this matters:**
When you provide your knowledge level and specific goals, the AI can:
- Tailor explanations to your expertise
- Focus on information that matters to your use case
- Skip over concepts you already know
- Provide more relevant chapter summaries and chat responses

The more context you give about **what you need**, the better the analysis will be.

## Requirements

- `yt-dlp` (for downloading video/transcript)
- API key for free models (optional - can delegate to another agent)

## Structure

```
sva/
├── SKILL.md              # Instructions for the agent
├── assets/               # HTML templates
│   └── template.html
├── scripts/              # Helper scripts
├── references/           # Reference documentation
└── analysis/             # Analysis results directory (created dynamically)
```

## Author

**Piotr Ratajski**  
https://ratajskipiotr.pl/

## License

MIT
