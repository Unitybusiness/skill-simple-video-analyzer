import sys
import re
import json

def parse_vtt_time(time_str):
    parts = time_str.replace(',', '.').split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return 0

def parse_vtt(filepath):
    transcript = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if '-->' in line:
                start_time = parse_vtt_time(line.split('-->')[0].strip())
                i += 1
                text_parts = []
                while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                    text_parts.append(re.sub(r'<[^>]+>', '', lines[i].strip()))
                    i += 1
                if text_parts:
                    transcript.append([start_time, ' '.join(text_parts)])
            else:
                i += 1
        return transcript
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: process.py <vtt_file>")
        sys.exit(1)
    
    res = parse_vtt(sys.argv[1])
    print(json.dumps(res, indent=2, ensure_ascii=False))
