#!/usr/bin/env python3
"""Generate architecture diagram for AutoWrite README.
Run when HiAPI key is unblocked."""
import urllib.request, json, sys

KEY = 'tWXRzt...cR'

prompt = (
    "IKEA manual style assembly diagram: AutoWrite book writing pipeline. "
    "Three connected stages left to right on white background: "
    "Stage 1: folder icon labeled 'Input Parser' with document layers, "
    "Stage 2: brain circuit icon labeled 'AI Engine', "
    "Stage 3: book with checkmark icon labeled 'Output Generator'. "
    "Thick black arrows connect each stage. "
    "Step numbers in circles at top of each card. "
    "Clean minimal line art, cream paper texture, "
    "black lines only with red accent for checkmark. "
    "No text except icon labels. "
    "Universal assembly instruction aesthetic."
)

req = urllib.request.Request(
    'https://api.hiapi.ai/v1/images/generations',
    data=json.dumps({
        'model': 'qwen-image-2.0',
        'prompt': prompt,
        'size': '1344x768'
    }).encode(),
    headers={'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'}
)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())
    url = data['data'][0]['url']
    print(f"SUCCESS: {url}")
    # Print the patch command ready to use
    print(f"\nPatch README with:")
    print(f"![Architecture]({url})")
except Exception as e:
    print(f"FAILED: {e}", file=sys.stderr)
    sys.exit(1)
