# ====================================================================================================

import requests
import json

# prompt  : string
# vendor  : ollama / openrouter / deepinfra
# history :
#    None -> Yield raw text
#    []   -> Yield history
def Process_LLM_streaming(prompt, vendor="ollama", history=None):
    prompt = prompt.strip()
    vendor = vendor.strip().lower()
    # --------------------------------------------------\
    LLM_API_KEY, LLM_API_URL, LLM_API_MDL = None, None, None
    if vendor=="ollama":
        LLM_API_KEY = "ollama"
        # LLM_API_URL = "http://192.168.80.99:11434/v1/chat/completions"
        LLM_API_URL = "http://192.168.20.62:11434/v1/chat/completions"
        LLM_API_MDL = "qwen2.5:7b"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "stream": True,
        "model": LLM_API_MDL,
        "messages": [{"role": "user", "content": prompt}],
        # # # LLM Parameters
        # "seed": 123456789,
        # "temperature": 0.5,          # Default: 1.0 [0.0 to 2.0]
        # "top_p": 1.0,                # Default: 1.0 [0.0 to 1.0]
        # "top_k": 0,                  # Default: 0   [0 or above]
        # "min_p": 0.0,                # Default: 0.0 [0.0 to 1.0]
        # "repetition_penalty": 1.0,   # Default: 1.0 [0.0 to 2.0]
        # "presence_penalty":   0.0,   # Default: 0.0 [-2.0 to 2.0]
        # "frequency_penalty":  0.0,   # Default: 0.0 [-2.0 to 2.0]
    }
    # --------------------------------------------------/
    # --------------------\
    if prompt == "":
        error_message = f"✨"
        yield error_message if history==None else history+[{"role":"assistant","content":error_message}]; return
    if not(LLM_API_KEY and LLM_API_URL and LLM_API_MDL):
        error_message = f"⚠️ LLM > Vendor not supported"
        yield error_message if history==None else history+[{"role":"assistant","content":error_message}]; return
    req = requests.post(LLM_API_URL, headers=headers, json=payload, stream=True)
    if req.status_code != 200:
        error_message = f"⚠️ LLM > status_code={req.status_code}"
        yield error_message if history==None else history+[{"role":"assistant","content":error_message}]; return
    # --------------------/
    try:
        # --------------------\
        if history == None:
            final_text = ""
        else:
            history.append({"role": "assistant", "content": ""})
        # --------------------/
        for line in req.iter_lines():
            if line:
                line = line.decode('utf-8', errors='replace')
                if line[:6] == "data: ":
                    line = line[6:]
                    if line == '[DONE]':
                        break
                    else:
                        try:
                            line = json.loads(line)
                            line = line["choices"][0]["delta"]["content"]
                            # print(line, end="")
                            # --------------------\
                            if history == None:
                                final_text += line
                                yield final_text
                            else:
                                history[-1]["content"] += line
                                yield history
                            # --------------------/
                        except:
                            pass
    finally:
        req.close()

def Process_LLM(prompt, vendor="ollama", history=None, streaming=False):
    stream = Process_LLM_streaming(prompt, vendor, history)
    if streaming:
        return stream
    else:
        res = None
        for e in stream:
            res = e
        return res