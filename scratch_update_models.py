import urllib.request
import json

try:
    req = urllib.request.urlopen('https://openrouter.ai/api/v1/models')
    data = json.loads(req.read().decode('utf-8'))
    api_free = [(m['id'], m['name']) for m in data['data'] if m['pricing']['prompt'] == '0' and m['pricing']['completion'] == '0']
except Exception as e:
    print("Error fetching:", e)
    api_free = []

old_free = [
    ('deepseek/deepseek-r1:free',                            'DeepSeek R1'),
    ('deepseek/deepseek-r1-distill-llama-70b:free',          'DeepSeek R1 Distill Llama 70B'),
    ('google/gemini-2.0-pro-exp-02-05:free',                 'Google Gemini 2.0 Pro Exp'),
    ('google/gemini-2.0-flash-thinking-exp:free',            'Google Gemini 2.0 Flash Thinking Exp'),
    ('google/gemini-2.0-flash-lite-preview-02-05:free',      'Google Gemini 2.0 Flash Lite Preview'),
    ('google/gemma-2-9b-it:free',                            'Google Gemma 2 9B'),
    ('meta-llama/llama-3.3-70b-instruct:free',               'Meta Llama 3.3 70B'),
    ('meta-llama/llama-3.2-3b-instruct:free',                'Meta Llama 3.2 3B'),
    ('meta-llama/llama-3.1-8b-instruct:free',                'Meta Llama 3.1 8B'),
    ('nvidia/llama-3.1-nemotron-70b-instruct:free',          'Nvidia Nemotron 70B'),
    ('qwen/qwen-2.5-72b-instruct:free',                      'Qwen 2.5 72B'),
    ('qwen/qwen-2.5-coder-32b-instruct:free',                'Qwen 2.5 Coder 32B'),
    ('mistralai/mistral-small-24b-instruct-2501:free',       'Mistral Small 24B'),
    ('mistralai/mistral-7b-instruct:free',                   'Mistral 7B'),
    ('cognitivecomputations/dolphin3.0-r1-mistral-24b:free', 'Dolphin 3.0 R1 Mistral 24B'),
    ('nousresearch/hermes-3-llama-3.1-405b:free',            'Nous Hermes 3 405B'),
    ('openchat/openchat-7b:free',                            'OpenChat 7B'),
    ('huggingfaceh4/zephyr-7b-beta:free',                    'Zephyr 7B Beta'),
]

seen_ids = set(m[0] for m in old_free)
for mid, mname in api_free:
    if mid not in seen_ids:
        name = mname.replace(' (free)', '')
        # Align spaces to make it neat
        old_free.append((mid, name))

out = '_OR_FREE_MODELS: list[tuple[str, str]] = [\n'
for mid, name in old_free:
    # pad mid to be nicely aligned if we want, or just standard string formatting
    out += f'    ("{mid}", "{name}"),\n'
out += ']\n'
print(out)
