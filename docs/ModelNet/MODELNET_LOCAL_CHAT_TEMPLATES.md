# ModelNet 本机 llama.cpp 对话模板盘点

- 生成时间：2026-05-18 17:17:54
- 扫描范围：`219.222.20.79:30000-32767`
- 查询方式：每个开放端口使用 `curl GET /props` 读取 `chat_template`，使用 `curl POST /apply-template` 渲染固定 system/user 测试消息，并用 `curl GET /v1/models` 读取服务模型名。
- 当前 Dify 机器：`/home/duxianghe/dify`，配置文件：`api/configs/model_net.yaml`

## 总览

- 发现 llama.cpp 模型服务端口：24 个
- 发现开放但非 llama.cpp 模型服务/无模板接口端口：5 个
- `model_net.yaml` 已配置端口：37 个
- 模型服务开放但未配置端口：2 个：`30293, 30297`
- 已配置但当前 `/props` 不通端口：15 个：`30459, 30498, 30586, 30587, 30689, 30782, 30784, 30786, 31136, 31323, 31464, 31926, 32310, 32520, 32767`

## DuetNet 当前 DSL alias 状态

当前 `DuetNet 显式循环 + 数据加载` DSL 使用 `q1=29`、`q2=5`、`g4=6`、`L3=2`。

| logical | alias id | port | registry model_name | status | template family |
|---|---:|---:|---|---|---|
| q1 | 29 | 30586 | `qwen25-3b-q8` | DOWN or /props unavailable | - |
| q2 | 5 | 32246 | `qwen25-7b-instruct-q5km` | alive | qwen/chatml |
| g4 | 6 | 31021 | `glm-4-9b-chat-q4k` | alive | glm |
| L3 | 2 | 30834 | `meta-llama-31-8b-instruct-q80` | alive | llama-3 |

## 已发现端口与模板状态

| port | registry id | registry model_name | server model_alias | template family | chat_format | template | apply-template | 本机配置判断 |
|---:|---|---|---|---|---|---|---|---|
| 30293 | - | - | `Qwen3-Embedding-8B-f16.gguf` | qwen/chatml | `Content-only` | len=2427 sha=44d5f08f3f72b837 | ok len=123 sha=7a404a07af2cb071 | not in model_net.yaml |
| 30297 | - | - | `embeddinggemma-300M-F32.gguf` | qwen/chatml | `Content-only` | len=208 sha=cc145ac597328b60 | ok len=123 sha=7a404a07af2cb071 | not in model_net.yaml |
| 30403 | 23 | hunyuan-7b-instruct-q5km | `tencent_Hunyuan-7B-Instruct-Q5_K_M.gguf` | hunyuan | `Content-only` | len=4919 sha=7dfb19355e3c8779 | ok len=98 sha=b9cd8f391c23d070 | server template available; registry has no pinned template metadata |
| 30465 | 18 | phi-4-mini-q8 | `Phi-4-mini-instruct.Q8_0.gguf` | phi | `Content-only` | len=398 sha=46bcd040271c497e | ok len=88 sha=cbb413705d324b61 | server template available; registry has no pinned template metadata |
| 30468 | 15 | gemma-3-4b-it-q4 | `gemma-3-4b-it-Q4_K_M.gguf` | gemma | `Content-only` | len=1531 sha=8d9e3a3c114fb205 | ok len=100 sha=45d43bb6ff1ddd31 | server template available; registry has no pinned template metadata |
| 30524 | 24 | ministral-3b-q8kxl | `Ministral-3-3B-Instruct-2512-UD-Q8_K_XL.gguf` | mistral/ministral | `Content-only` | len=7503 sha=a81fa42ad89f88c7 | ok len=87 sha=c8d8b5b82a9a3b6e | server template available; registry has no pinned template metadata |
| 30525 | 16 | granite-h-micro-3b-q8kxl | `granite-4.0-h-micro-UD-Q8_K_XL.gguf` | granite | `Content-only` | len=6418 sha=9524df67b77a7b25 | ok len=190 sha=d021d4f0534a597f | server template available; registry has no pinned template metadata |
| 30526 | 3 | gemma4-e2b-q8 | `gemma-4-E2B-it-Q8_0.gguf` | gemma | `Content-only` | len=16317 sha=781d10940fbc44be | ok len=108 sha=655d3fc903900db0 | server template available; registry has no pinned template metadata |
| 30528 | 10 | gemma4-e4b-q8kxl | `gemma-4-E4B-it-UD-Q8_K_XL.gguf` | gemma | `Content-only` | len=11926 sha=55572b8d3c834204 | ok len=107 sha=0b10e4d934663594 | server template available; registry has no pinned template metadata |
| 30578 | 22 | qwen3-8b-bf16 | `Qwen3-8B-BF16.gguf` | qwen/chatml | `Content-only` | len=4905 sha=5da44855ab7e0641 | ok len=123 sha=7a404a07af2cb071 | server template available; registry has no pinned template metadata |
| 30582 | 32 | qwen3-8b-bf16 | `Qwen3-8B-BF16.gguf` | qwen/chatml | `Content-only` | len=4905 sha=5da44855ab7e0641 | ok len=123 sha=7a404a07af2cb071 | server template available; registry has no pinned template metadata |
| 30584 | 14 | qwen3-4b-instruct-2507-q4km | `Qwen3-4B-Instruct-2507-Q4_K_M.gguf` | qwen/chatml | `Content-only` | len=4051 sha=c979e0e71a3e21b8 | ok len=123 sha=7a404a07af2cb071 | server template available; registry has no pinned template metadata |
| 30788 | 38 | gpt-oss-20b-mxfp4 | `gpt-oss-20b-mxfp4.gguf` | gpt-oss | `Content-only` | len=14580 sha=0f1b6cb32273ad2a | ok len=466 sha=7bb4b3756d07f909 | server template available; registry has no pinned template metadata |
| 30834 | 2 | meta-llama-31-8b-instruct-q80 | `Llama-3.1-8B-Instruct-Q8_0.gguf` | llama-3 | `Content-only` | len=4613 sha=93c0e9aa3629bbd7 | ok len=289 sha=8df0c197e1667aae | server template available; registry has no pinned template metadata |
| 30905 | 8 | hunyuan-7b-instruct-q5km | `tencent_Hunyuan-7B-Instruct-Q5_K_M.gguf` | hunyuan | `Content-only` | len=4919 sha=7dfb19355e3c8779 | ok len=98 sha=b9cd8f391c23d070 | server template available; registry has no pinned template metadata |
| 30920 | 34 | gemma-3-27b-it-q4 | `gemma-3-27b-it-Q4_K_M.gguf` | gemma | `Content-only` | len=1532 sha=7de1c58e208eda46 | ok len=100 sha=45d43bb6ff1ddd31 | server template available; registry has no pinned template metadata |
| 30926 | 33 | qwen35-9b-q8kxl | `Qwen3.5-9B-UD-Q8_K_XL.gguf` | qwen/chatml | `Content-only` | len=7816 sha=7f0e529032c25183 | ok len=131 sha=eccfed9a9c4a2fa4 | server template available; registry has no pinned template metadata |
| 30927 | 39 | qwen35-9b-q8kxl | `Qwen3.5-9B-UD-Q8_K_XL.gguf` | qwen/chatml | `Content-only` | len=7816 sha=7f0e529032c25183 | ok len=131 sha=eccfed9a9c4a2fa4 | server template available; registry has no pinned template metadata |
| 31021 | 6 | glm-4-9b-chat-q4k | `glm-4-9b-chat.Q4_K.gguf` | glm | `Content-only` | len=544 sha=fbd6f678a56640d9 | ok len=89 sha=08a99427e6cb9c0c | server template available; registry has no pinned template metadata |
| 31329 | 19 | kimi-vl-a3b-instruct-q4km | `Kimi-VL-A3B-Instruct.Q4_K_M.gguf` | kimi | `Content-only` | len=907 sha=8452948e3156f904 | ok len=161 sha=6f264cec2b359859 | server template available; registry has no pinned template metadata |
| 31466 | 13 | glm-4-9b-chat-q4k | `glm-4-9b-chat.Q4_K.gguf` | glm | `Content-only` | len=544 sha=fbd6f678a56640d9 | ok len=89 sha=08a99427e6cb9c0c | server template available; registry has no pinned template metadata |
| 31541 | 21 | qwen25-7b-instruct-q5km | `qwen2.5-7b-instruct-q5_k_m.gguf` | qwen/chatml | `Content-only` | len=2509 sha=d5495a1e5db06111 | ok len=123 sha=7a404a07af2cb071 | server template available; registry has no pinned template metadata |
| 32246 | 5 | qwen25-7b-instruct-q5km | `qwen2.5-7b-instruct-q5_k_m.gguf` | qwen/chatml | `Content-only` | len=2508 sha=4e9918361c284a93 | ok len=123 sha=7a404a07af2cb071 | server template available; registry has no pinned template metadata |
| 32685 | 7 | meta-llama-31-8b-instruct-q80 | `Llama-3.1-8B-Instruct-Q8_0.gguf` | llama-3 | `Content-only` | len=4613 sha=93c0e9aa3629bbd7 | ok len=289 sha=8df0c197e1667aae | server template available; registry has no pinned template metadata |

## 已配置但当前不可达

| port | registry id | registry model_name | model_url |
|---:|---|---|---|
| 30459 | 17 | `phi-4-mini-bf16` | `http://219.222.20.79:30459` |
| 30498 | 26 | `gemma-3-4b-it-q4` | `http://219.222.20.79:30498` |
| 30586 | 29 | `qwen25-3b-q8` | `http://219.222.20.79:30586` |
| 30587 | 28 | `llama32-3b-q8` | `http://219.222.20.79:30587` |
| 30689 | 30 | `qwen25-7b-instruct-q5km` | `http://219.222.20.79:30689` |
| 30782 | 37 | `qwen35-27b-q6kxl` | `http://219.222.20.79:30782` |
| 30784 | 35 | `gpt-oss-20b-mxfp4` | `http://219.222.20.79:30784` |
| 30786 | 36 | `ministral-14b` | `http://219.222.20.79:30786` |
| 31136 | 1 | `gpt-oss-20b-mxfp4` | `http://219.222.20.79:31136` |
| 31323 | 20 | `kimi-vl-a3b-thinking-2506-q4km` | `http://219.222.20.79:31323` |
| 31464 | 11 | `glm-4-9b-chat-q4k` | `http://219.222.20.79:31464` |
| 31926 | 4 | `hunyuan-7b-instruct-q5km` | `http://219.222.20.79:31926` |
| 32310 | 27 | `deepseek-r1-distill-qwen-7b-q4` | `http://219.222.20.79:32310` |
| 32520 | 31 | `qwen3-30b-a3b-instruct-2507-q5km` | `http://219.222.20.79:32520` |
| 32767 | 9 | `qwen25-7b-instruct-q5km` | `http://219.222.20.79:32767` |

## 模型服务开放但未写入 model_net.yaml

| port | server model_alias | v1 model | template family | EOS/stop 需要人工确认 |
|---:|---|---|---|---|
| 30293 | `Qwen3-Embedding-8B-f16.gguf` | `Qwen3-Embedding-8B-f16.gguf` | qwen/chatml | 是 |
| 30297 | `embeddinggemma-300M-F32.gguf` | `embeddinggemma-300M-F32.gguf` | qwen/chatml | 是 |

## 开放但非 llama.cpp 模型服务或无模板接口

| port | /props 响应摘要 | apply-template 响应摘要 |
|---:|---|---|
| 31063 | no `model_alias/model_path/chat_template` in `/props` | `{"detail": "Not Found"}` |
| 31309 | no `model_alias/model_path/chat_template` in `/props` | `{"detail": "Not Found"}` |
| 31362 | no `model_alias/model_path/chat_template` in `/props` | `{"code": 401, "data": null, "msg": "账号未登录"}` |
| 31404 | no `model_alias/model_path/chat_template` in `/props` | `{"detail": "Not Found"}` |
| 32649 | no `model_alias/model_path/chat_template` in `/props` | `{"detail": "Not Found"}` |

## 对开发机的配置建议

1. 当前运行时依赖 llama.cpp 的 `POST /apply-template`；`model_net.yaml` 只保存 `model_url/EOS/type/stop_think/expose_raw_logits`，没有保存或校验 `chat_template`。
2. 建议后续开发把 `/props.chat_template` 的 `sha256`、模板族、`/apply-template` 渲染样例加入模型探测/校验结果，至少在导入或点击“Fetch model info”时提示模板缺失、模板族未知、服务不可达。
3. 对 DuetNet 严格 raw-logit 工作流，除模板外还要确认对应端口是 raw-logit fork；当前 `model_net.yaml` 只有少数 alias 设置 `expose_raw_logits: true`。
4. `chat_format: Content-only` 在这些服务上不等于没有模板；以 `/props.chat_template` 和 `/apply-template` 实际渲染结果为准。

## curl 查询命令样例

```text
curl -sS --max-time 3 http://219.222.20.79:30905/props

curl -sS --max-time 3 -H "Content-Type: application/json" \
  --data-binary '{"messages":[{"role":"system","content":"You are a concise assistant."},{"role":"user","content":"Answer with OK."}]}' \
  http://219.222.20.79:30905/apply-template
```

## 逐端口详情

### 30293 - Qwen3-Embedding-8B-f16.gguf

配置：未写入 `model_net.yaml`。

- server model_alias: `Qwen3-Embedding-8B-f16.gguf`
- v1 model: `Qwen3-Embedding-8B-f16.gguf`
- model_path: `/data/models/Qwen3-Embedding-8B-f16.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=2427 sha256=44d5f08f3f72b837 family=qwen/chatml flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=123 sha256=7a404a07af2cb071

渲染样例：
```text
<|im_start|>system
You are a concise assistant.<|im_end|>
<|im_start|>user
Answer with OK.<|im_end|>
<|im_start|>assistant
```

完整 chat_template：
```text
{%- if tools %}
    {{- '<|im_start|>system\n' }}
    {%- if messages[0]['role'] == 'system' %}
        {{- messages[0]['content'] }}
    {%- else %}
        {{- 'You are a helpful assistant.' }}
    {%- endif %}
    {{- "\n\n# Tools\n\nYou may call one or more functions to assist with the user query.\n\nYou are provided with function signatures within <tools></tools> XML tags:\n<tools>" }}
    {%- for tool in tools %}
        {{- "\n" }}
        {{- tool | tojson }}
    {%- endfor %}
    {{- "\n</tools>\n\nFor each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\n<tool_call>\n{\"name\": <function-name>, \"arguments\": <args-json-object>}\n</tool_call><|im_end|>\n" }}
{%- else %}
    {%- if messages[0]['role'] == 'system' %}
        {{- '<|im_start|>system\n' + messages[0]['content'] + '<|im_end|>\n' }}
    {%- else %}
        {{- '<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n' }}
    {%- endif %}
{%- endif %}
{%- for message in messages %}
    {%- if (message.role == "user") or (message.role == "system" and not loop.first) or (message.role == "assistant" and not message.tool_calls) %}
        {{- '<|im_start|>' + message.role + '\n' + message.content + '<|im_end|>' + '\n' }}
    {%- elif message.role == "assistant" %}
        {{- '<|im_start|>' + message.role }}
        {%- if message.content %}
            {{- '\n' + message.content }}
        {%- endif %}
        {%- for tool_call in message.tool_calls %}
            {%- if tool_call.function is defined %}
                {%- set tool_call = tool_call.function %}
            {%- endif %}
            {{- '\n<tool_call>\n{"name": "' }}
            {{- tool_call.name }}
            {{- '", "arguments": ' }}
            {{- tool_call.arguments | tojson }}
            {{- '}\n</tool_call>' }}
        {%- endfor %}
        {{- '<|im_end|>\n' }}
    {%- elif message.role == "tool" %}
        {%- if (loop.index0 == 0) or (messages[loop.index0 - 1].role != "tool") %}
            {{- '<|im_start|>user' }}
        {%- endif %}
        {{- '\n<tool_response>\n' }}
        {{- message.content }}
        {{- '\n</tool_response>' }}
        {%- if loop.last or (messages[loop.index0 + 1].role != "tool") %}
            {{- '<|im_end|>\n' }}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
    {{- '<|im_start|>assistant\n' }}
{%- endif %}

```

### 30297 - embeddinggemma-300M-F32.gguf

配置：未写入 `model_net.yaml`。

- server model_alias: `embeddinggemma-300M-F32.gguf`
- v1 model: `embeddinggemma-300M-F32.gguf`
- model_path: `/data/models/embeddinggemma-300M-F32.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=208 sha256=cc145ac597328b60 family=qwen/chatml flags={'has_system': False, 'has_user': False, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=123 sha256=7a404a07af2cb071

渲染样例：
```text
<|im_start|>system
You are a concise assistant.<|im_end|>
<|im_start|>user
Answer with OK.<|im_end|>
<|im_start|>assistant
```

完整 chat_template：
```text
{%- for message in messages -%}
  {{- '<|im_start|>' + message.role + '
' + message.content + '<|im_end|>
' -}}
{%- endfor -%}
{%- if add_generation_prompt -%}
  {{- '<|im_start|>assistant
' -}}
{%- endif -%}
```

### 30403 - tencent_Hunyuan-7B-Instruct-Q5_K_M.gguf

配置：
- id `23`：`hunyuan-7b-instruct-q5km`，type=`normal`，EOS=`<|eos|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `tencent_Hunyuan-7B-Instruct-Q5_K_M.gguf`
- v1 model: `tencent_Hunyuan-7B-Instruct-Q5_K_M.gguf`
- model_path: `/data/models/tencent_Hunyuan-7B-Instruct-Q5_K_M.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=4919 sha256=7dfb19355e3c8779 family=hunyuan flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=98 sha256=b9cd8f391c23d070

渲染样例：
```text
<|startoftext|>You are a concise assistant.<|extra_4|>Answer with OK.<|extra_0|><think>

</think>
```

完整 chat_template：
```text
{%- if not add_generation_prompt is defined %}
    {%- set add_generation_prompt = false %}
{%- endif %}
{%- set ns = namespace(is_first=false, is_tool=false, is_output_first=true, system_prompt='', is_first_sp=true, is_first_user=true, is_last_user=false) %}
{%- for message in messages %}
    {%- if message['role'] == 'system' %}
        {%- if ns.is_first_sp %}
            {%- set ns.system_prompt = ns.system_prompt + message['content'] %}
            {%- set ns.is_first_sp = false %}
        {%- else %}
            {%- set ns.system_prompt = ns.system_prompt + '

' + message['content'] %}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{{- bos_token }}
{{- ns.system_prompt }}
{%- if tools %}
    {%- if ns.system_prompt != '' %}
        {{- '

# Tools

You may call one or more functions to assist with the user query.' }}
    {%- else %}
        {{- '# Tools

You may call one or more functions to assist with the user query.' }}
    {%- endif %}
    {{- '

You are provided with function signatures within <tools></tools> XML tags:' }}
    {{- '
<tools>
' }}
    {%- for tool in tools %}
        {%- if loop.index0 > 0 %}
            {{- '
' }}
        {%- endif %}
        {{- tool | tojson }}
    {%- endfor %}
    {{- '
</tools>

' }}
    {{- 'For function call returns, you should first print <tool_calls>' }}
    {{- 'For each function call, you should return object like:
' }}
    {{- '<tool_call>function_name
` ` `json
function_arguments_in_json_format
` ` `</tool_call>' }}
    {{- 'At the end of function call returns, you should print </tool_calls>' }}
{%- endif %}
{%- if ns.system_prompt != '' or tools %}
    {{- '<|extra_4|>' }}
{%- endif %}
{%- for message in messages %}
    {%- if message['role'] == 'user' %}
        {%- set ns.is_tool = false %}
        {%- set ns.is_first = false %}
        {%- set ns.is_last_user = true %}
        {%- if ns.is_first_user %}
            {{- message['content'] + '<|extra_0|>' }}
            {%- set ns.is_first_user = false %}
        {%- else %}
            {{- bos_token + message['content'] + '<|extra_0|>' }}
        {%- endif %}
    {%- endif %}
    {%- if message['role'] == 'assistant' and message['tool_calls'] is defined and message['tool_calls'] is not none %}
        {%- set ns.is_last_user = false %}
        {%- if ns.is_tool %}
            {{- '</tool_responses>' + '<|extra_0|>' }}
        {%- endif %}
        {%- set ns.is_first = false %}
        {%- set ns.is_tool = false %}
        {%- set ns.is_output_first = true %}
        {%- for tool in message['tool_calls'] %}
            {%- set arguments = tool['function']['arguments'] %}
            {%- if arguments is not string %}
                {%- set arguments = arguments | tojson %}
            {%- endif %}
            {%- if not ns.is_first %}
                {%- if message['content'] is none %}
                    {{- '<tool_calls><tool_call>' + tool['function']['name'] + '
' + '` ` `json' + '
' + arguments + '
' + '` ` `' + '</tool_call>' }}
                {%- else %}
                    {{- message['content'] + '<tool_calls><tool_call>' + tool['function']['name'] + '
' + '` ` `json' + '
' + arguments + '
' + '` ` `' + '</tool_call>' }}
                {%- endif %}
            {%- set ns.is_first = true %}
            {%- else %}
                {{- '
' + '<tool_call>' + tool['function']['name'] + '
' + '` ` `json' + '
' + arguments + '
' + '` ` `' + '</tool_call>' }}
            {%- endif %}
        {%- endfor %}
        {{- '</tool_calls>' + eos_token }}
    {%- endif %}
    {%- if message['role'] == 'assistant' and (message['tool_calls'] is not defined or message['tool_calls'] is none) %}
        {%- set content = message['content'] %}
        {%- if '<answer>' in content and not loop.last %}
            {%- set content = content.split('<answer>')[-1].strip('</answer>').strip() %}
        {%- endif %}
        {%- set ns.is_last_user = false %}
        {%- if ns.is_tool %}
            {{- '</tool_responses>' + '<|extra_0|>' + content + eos_token }}
            {%- set ns.is_tool = false %}
        {%- else %}
            {{- content + eos_token }}
        {%- endif %}
    {%- endif %}
    {%- if message['role'] == 'tool' %}
        {%- set ns.is_last_user = false %}
        {%- set ns.is_tool = true %}
        {%- if ns.is_output_first %}
            {{- bos_token + '<tool_responses><tool_response>' + message['content'] + '</tool_response>' }}
            {%- set ns.is_output_first = false %}
        {%- else %}
            {{- '
<tool_response>' + message['content'] + '</tool_response>' }}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{%- if ns.is_tool %}
    {{- '</tool_responses>' + '<|extra_0|>' }}
{%- endif %}
{%- if add_generation_prompt and not ns.is_last_user and not ns.is_tool %}
    {{- '<|extra_0|>' }}
{%- endif %}
{%- if enable_thinking is defined and not enable_thinking %}
    {{- '<think>

</think>
' }}
{%- endif %}
```

### 30465 - Phi-4-mini-instruct.Q8_0.gguf

配置：
- id `18`：`phi-4-mini-q8`，type=`normal`，EOS=`<|end|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `Phi-4-mini-instruct.Q8_0.gguf`
- v1 model: `Phi-4-mini-instruct.Q8_0.gguf`
- model_path: `/data/models/Phi-4-mini-instruct.Q8_0.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=398 sha256=46bcd040271c497e family=phi flags={'has_system': True, 'has_user': False, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=88 sha256=cbb413705d324b61

渲染样例：
```text
<|system|>You are a concise assistant.<|end|><|user|>Answer with OK.<|end|><|assistant|>
```

完整 chat_template：
```text
{% for message in messages %}{% if message['role'] == 'system' and 'tools' in message and message['tools'] is not none %}{{ '<|' + message['role'] + '|>' + message['content'] + '<|tool|>' + message['tools'] + '<|/tool|>' + '<|end|>' }}{% else %}{{ '<|' + message['role'] + '|>' + message['content'] + '<|end|>' }}{% endif %}{% endfor %}{% if add_generation_prompt %}{{ '<|assistant|>' }}{% endif %}
```

### 30468 - gemma-3-4b-it-Q4_K_M.gguf

配置：
- id `15`：`gemma-3-4b-it-q4`，type=`normal`，EOS=`<|end_of_text|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `gemma-3-4b-it-Q4_K_M.gguf`
- v1 model: `gemma-3-4b-it-Q4_K_M.gguf`
- model_path: `/data/models/gemma-3-4b-it-Q4_K_M.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=1531 sha256=8d9e3a3c114fb205 family=gemma flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=100 sha256=45d43bb6ff1ddd31

渲染样例：
```text
<start_of_turn>user
You are a concise assistant.

Answer with OK.<end_of_turn>
<start_of_turn>model
```

完整 chat_template：
```text
{{ bos_token }}
{%- if messages[0]['role'] == 'system' -%}
    {%- if messages[0]['content'] is string -%}
        {%- set first_user_prefix = messages[0]['content'] + '

' -%}
    {%- else -%}
        {%- set first_user_prefix = messages[0]['content'][0]['text'] + '

' -%}
    {%- endif -%}
    {%- set loop_messages = messages[1:] -%}
{%- else -%}
    {%- set first_user_prefix = "" -%}
    {%- set loop_messages = messages -%}
{%- endif -%}
{%- for message in loop_messages -%}
    {%- if (message['role'] == 'user') != (loop.index0 % 2 == 0) -%}
        {{ raise_exception("Conversation roles must alternate user/assistant/user/assistant/...") }}
    {%- endif -%}
    {%- if (message['role'] == 'assistant') -%}
        {%- set role = "model" -%}
    {%- else -%}
        {%- set role = message['role'] -%}
    {%- endif -%}
    {{ '<start_of_turn>' + role + '
' + (first_user_prefix if loop.first else "") }}
    {%- if message['content'] is string -%}
        {{ message['content'] | trim }}
    {%- elif message['content'] is iterable -%}
        {%- for item in message['content'] -%}
            {%- if item['type'] == 'image' -%}
                {{ '<start_of_image>' }}
            {%- elif item['type'] == 'text' -%}
                {{ item['text'] | trim }}
            {%- endif -%}
        {%- endfor -%}
    {%- else -%}
        {{ raise_exception("Invalid content type") }}
    {%- endif -%}
    {{ '<end_of_turn>
' }}
{%- endfor -%}
{%- if add_generation_prompt -%}
    {{'<start_of_turn>model
'}}
{%- endif -%}
```

### 30524 - Ministral-3-3B-Instruct-2512-UD-Q8_K_XL.gguf

配置：
- id `24`：`ministral-3b-q8kxl`，type=`normal`，EOS=`</s>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `Ministral-3-3B-Instruct-2512-UD-Q8_K_XL.gguf`
- v1 model: `Ministral-3-3B-Instruct-2512-UD-Q8_K_XL.gguf`
- model_path: `/data/models/Ministral-3-3B-Instruct-2512-UD-Q8_K_XL.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=7503 sha256=a81fa42ad89f88c7 family=mistral/ministral flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': False}
- apply-template: ok len=87 sha256=c8d8b5b82a9a3b6e

渲染样例：
```text
[SYSTEM_PROMPT]You are a concise assistant.[/SYSTEM_PROMPT][INST]Answer with OK.[/INST]
```

完整 chat_template：
```text
{#- Unsloth template fixes #}
{#- Default system message if no system prompt is passed. #}
{%- set default_system_message = 'You are Ministral-3-3B-Instruct-2512, a Large Language Model (LLM) created by Mistral AI, a French startup headquartered in Paris.\nYou power an AI assistant called Le Chat.\nYour knowledge base was last updated on 2023-10-01.\nThe current date is {today}.\n\nWhen you\'re not sure about some information or when the user\'s request requires up-to-date or specific data, you must use the available tools to fetch the information. Do not hesitate to use tools whenever they can provide a more accurate or complete response. If no relevant tools are available, then clearly state that you don\'t have the information and avoid making up anything.\nIf the user\'s question is not clear, ambiguous, or does not provide enough context for you to accurately answer the question, you do not try to answer it right away and you rather ask the user to clarify their request (e.g. "What are some good restaurants around me?" => "Where are you?" or "When is the next flight to Tokyo" => "Where do you travel from?").\nYou are always very attentive to dates, in particular you try to resolve dates (e.g. "yesterday" is {yesterday}) and when asked about information at specific dates, you discard information that is at another date.\nYou follow these instructions in all languages, and always respond to the user in the language they use or request.\nNext sections describe the capabilities that you have.\n\n# WEB BROWSING INSTRUCTIONS\n\nYou cannot perform any web search or access internet to open URLs, links etc. If it seems like the user is expecting you to do so, you clarify the situation and ask the user to copy paste the text directly in the chat.\n\n# MULTI-MODAL INSTRUCTIONS\n\nYou have the ability to read images, but you cannot generate images. You also cannot transcribe audio files or videos.\nYou cannot read nor transcribe audio files or videos.\n\n# TOOL CALLING INSTRUCTIONS\n\nYou may have access to tools that you can use to fetch information or perform actions. You must use these tools in the following situations:\n\n1. When the request requires up-to-date information.\n2. When the request requires specific data that you do not have in your knowledge base.\n3. When the request involves actions that you cannot perform without tools.\n\nAlways prioritize using tools to provide the most accurate and helpful response. If tools are not available, inform the user that you cannot perform the requested action at the moment.' %}

{#- Begin of sequence token. #}
{{- bos_token }}

{#- Handle system prompt if it exists. #}
{#- System prompt supports text content or text chunks. #}
{%- if messages[0]['role'] == 'system' %}
    {{- '[SYSTEM_PROMPT]' -}}
    {%- if messages[0]['content'] is string %}
        {{- messages[0]['content'] -}}
    {%- else %}        
        {%- for block in messages[0]['content'] %}
            {%- if block['type'] == 'text' %}
                {{- block['text'] }}
            {%- else %}
                {{- raise_exception('Only text chunks are supported in system message contents.') }}
            {%- endif %}
        {%- endfor %}
    {%- endif %}
    {{- '[/SYSTEM_PROMPT]' -}}
    {%- set loop_messages = messages[1:] %}
{%- else %}
    {%- set loop_messages = messages %}
    {%- if default_system_message != '' %}
        {{- '[SYSTEM_PROMPT]' + default_system_message + '[/SYSTEM_PROMPT]' }}
    {%- endif %}
{%- endif %}


{#- Tools definition #}
{%- set tools_definition = '' %}
{%- set has_tools = false %}
{%- if tools is defined and tools is not none and tools|length > 0 %}
    {%- set has_tools = true %}
    {%- set tools_definition = '[AVAILABLE_TOOLS]' + (tools| tojson) + '[/AVAILABLE_TOOLS]' %}
    {{- tools_definition }}
{%- endif %}

{#- Checks for alternating user/assistant messages. #}
{%- set ns = namespace(index=0) %}
{%- for message in loop_messages %}
    {%- if message.role == 'user' or (message.role == 'assistant' and (message.tool_calls is not defined or message.tool_calls is none or message.tool_calls | length == 0)) %}
        {%- if (message['role'] == 'user') != (ns.index % 2 == 0) %}
            {{- raise_exception('After the optional system message, conversation roles must alternate user and assistant roles except for tool calls and results.') }}
        {%- endif %}
        {%- set ns.index = ns.index + 1 %}
    {%- endif %}
{%- endfor %}

{#- Handle conversation messages. #}
{%- for message in loop_messages %}

    {#- User messages supports text content or text and image chunks. #}
    {%- if message['role'] == 'user' %}
        {%- if message['content'] is string %}
            {{- '[INST]' + message['content'] + '[/INST]' }}
        {%- elif message['content'] | length > 0 %}
            {{- '[INST]' }}
            {%- if message['content'] | length == 2 %}
                {%- set blocks = message['content'] | sort(attribute='type') %}
            {%- else %}
                {%- set blocks = message['content'] %}
            {%- endif %}
            {%- for block in blocks %}
                {%- if block['type'] == 'text' %}
                    {{- block['text'] }}
                {%- elif block['type'] in ['image', 'image_url'] %}
                    {{- '[IMG]' }}
                {%- else %}
                    {{- raise_exception('Only text, image and image_url chunks are supported in user message content.') }}
                {%- endif %}
            {%- endfor %}
            {{- '[/INST]' }}
        {%- else %}
            {{- raise_exception('User message must have a string or a list of chunks in content') }}
        {%- endif %}

    {#- Assistant messages supports text content or text and image chunks. #}
    {%- elif message['role'] == 'assistant' %}

        {%- if message['content'] is string %}
            {{- message['content'] }}
        {%- elif message['content'] is iterable and message['content'] | length > 0 %}
            {%- for block in message['content'] %}
                {%- if block['type'] == 'text' %}
                    {{- block['text'] }}
                {%- else %}
                    {{- raise_exception('Only text chunks are supported in assistant message contents.') }}
                {%- endif %}
            {%- endfor %}
        {%- endif %}
        
        {%- if message['tool_calls'] is defined and message['tool_calls'] is not none and message['tool_calls']|length > 0 %}
            {%- for tool in message['tool_calls'] %}
                {%- set arguments = tool['function']['arguments'] %}
                {%- if arguments is not string %}
                    {%- set arguments = arguments|tojson|safe %}
                {%- elif arguments == '' %}
                    {%- set arguments = '{}' %}
                {%- endif %}
                {{- '[TOOL_CALLS]' + tool['function']['name'] + '[ARGS]' + arguments }}
            {%- endfor %}
        {%- endif %}

        {#- End of sequence token for each assistant messages. #}
        {{- eos_token }}

    {#- Tool messages only supports text content. #}
    {%- elif message['role'] == 'tool' %}
        {{- '[TOOL_RESULTS]' + message['content']|string + '[/TOOL_RESULTS]' }}

    {#- Raise exception for unsupported roles. #}
    {%- else %}
        {{- raise_exception('Only user, assistant and tool roles are supported, got ' + message['role']) }}
    {%- endif %}
{%- endfor %}

{#- Copyright 2025-present Unsloth. Apache 2.0 License. #}
```

### 30525 - granite-4.0-h-micro-UD-Q8_K_XL.gguf

配置：
- id `16`：`granite-h-micro-3b-q8kxl`，type=`normal`，EOS=`<|end_of_text|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `granite-4.0-h-micro-UD-Q8_K_XL.gguf`
- v1 model: `granite-4.0-h-micro-UD-Q8_K_XL.gguf`
- model_path: `/data/models/granite-4.0-h-micro-UD-Q8_K_XL.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=6418 sha256=9524df67b77a7b25 family=granite flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=190 sha256=d021d4f0534a597f

渲染样例：
```text
<|start_of_role|>system<|end_of_role|>You are a concise assistant.<|end_of_text|>
<|start_of_role|>user<|end_of_role|>Answer with OK.<|end_of_text|>
<|start_of_role|>assistant<|end_of_role|>
```

完整 chat_template：
```text
{%- set tools_system_message_prefix = 'You are a helpful assistant with access to the following tools. You may call one or more tools to assist with the user query.\n\nYou are provided with function signatures within <tools></tools> XML tags:\n<tools>'  %}
{%- set tools_system_message_suffix = '\n</tools>\n\nFor each tool call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\n<tool_call>\n{\"name\": <function-name>, \"arguments\": <args-json-object>}\n</tool_call>. If a tool does not exist in the provided list of tools, notify the user that you do not have the ability to fulfill the request.' %}
{%- set documents_system_message_prefix = 'You are a helpful assistant with access to the following documents. You may use one or more documents to assist with the user query.\n\nYou are given a list of documents within <documents></documents> XML tags:\n<documents>' %}
{%- set documents_system_message_suffix = '\n</documents>\n\nWrite the response to the user\'s input by strictly aligning with the facts in the provided documents. If the information needed to answer the question is not available in the documents, inform the user that the question cannot be answered based on the available data.' %}
{%- set g4_default_system_message = 'You are a helpful assistant. Please ensure responses are professional, accurate, and safe.' %}
{%- if available_tools is defined and available_tools %}
    {%- set tools = available_tools %}
{%- endif %}
{%- set ns = namespace(tools_system_message=tools_system_message_prefix,
                       documents_system_message=documents_system_message_prefix,
                       default_system_message=g4_default_system_message,
                       system_message=''
                       ) %}
{%- if tools %}
    {%- for tool in tools %}
        {%- set ns.tools_system_message = ns.tools_system_message + '\n' + (tool | tojson) %}
    {%- endfor %}
    {%- set ns.tools_system_message = ns.tools_system_message + tools_system_message_suffix %}
{%- else %}
    {%- set ns.tools_system_message = '' %}
{%- endif %}
{%- if documents %}
    {%- for document in documents %}
        {%- set ns.documents_system_message = ns.documents_system_message + '\n' + (document | tojson) %}
    {%- endfor %}
    {%- set ns.documents_system_message = ns.documents_system_message + documents_system_message_suffix %}
{%- else %}
    {%- set ns.documents_system_message = '' %}
{%- endif %}
{%- if messages[0].role == 'system' %}
    {%- if messages[0].content is string %}
        {%- set ns.system_message = messages[0].content %}
    {%- elif messages[0].content is iterable %}
        {%- for entry in messages[0].content %}
            {%- if entry.type== 'text' %}
                {%- if ns.system_message != '' %}
                    {%- set ns.system_message = ns.system_message + '\n' %}
                {%- endif %}
                {%- set ns.system_message = ns.system_message + entry.text %}
            {%- endif %}
        {%- endfor %}
    {%- endif %}
    {%- if tools and documents %}
        {%- set ns.system_message = ns.system_message + '\n\n' +  ns.tools_system_message + '\n\n' + ns.documents_system_message %}
    {%- elif tools %}
        {%- set ns.system_message = ns.system_message + '\n\n' + ns.tools_system_message %}
    {%- elif documents %}
        {%- set ns.system_message = ns.system_message + '\n\n' + ns.documents_system_message %}
    {%- endif %}
{%- else %}
    {%- if tools and documents %}
        {%- set ns.system_message = ns.tools_system_message + '\n\n' + ns.documents_system_message  %}
    {%- elif tools %}
        {%- set ns.system_message = ns.tools_system_message %}
    {%- elif documents %}
        {%- set ns.system_message = ns.documents_system_message %}
    {%- endif %}
{%- endif %}
{%- if ns.system_message %}
    {{- '<|start_of_role|>system<|end_of_role|>' + ns.system_message + '<|end_of_text|>\n' }}
{%- else %}
    {{- '<|start_of_role|>system<|end_of_role|>' + ns.default_system_message + '<|end_of_text|>\n' }}
{%- endif %}
{%- for message in messages %}
    {%- set content = namespace(val='') %}
    {%- if message.content is string %}
        {%- set content.val = message.content %}
    {%- else %}
        {%- if message.content is iterable %}
            {%- for entry in message.content %}
                {%- if entry.type== 'text' %}
                    {%- if content.val != '' %}
                        {%- set content.val = content.val + '\n' %}
                    {%- endif %}
                    {%- set content.val = content.val + entry.text %}
                {%- endif %}
            {%- endfor %}
        {%- endif %}
    {%- endif %}
    {%- if (message.role == 'user') or (message.role == 'system' and not loop.first) %}
        {{- '<|start_of_role|>' + message.role + '<|end_of_role|>' + content.val + '<|end_of_text|>\n' }}
    {%- elif message.role == 'assistant' %}
        {{- '<|start_of_role|>' + message.role + '<|end_of_role|>' + content.val }}
        {%- if message.tool_calls %}
            {%- for tool_call in message.tool_calls %}
                {%- if (loop.first and content.val) or (not loop.first) %}
                    {{- '\n' }}
                {%- endif %}
                {%- if tool_call.function %}
                    {%- set tool_call = tool_call.function %}
                {%- endif %}
                {{- '<tool_call>\n{"name": "' }}
                {{- tool_call.name }}
                {{- '", "arguments": ' }}
                {%- if tool_call.arguments is string %}
                    {{- tool_call.arguments }}
                {%- else %}
                    {{- tool_call.arguments | tojson }}
                {%- endif %}
                {{- '}\n</tool_call>' }}
            {%- endfor %}
        {%- endif %}
        {{- '<|end_of_text|>\n' }}
    {%- elif message.role == 'tool' %}
        {%- if loop.first or (messages[loop.index0 - 1].role != 'tool') %}
            {{- '<|start_of_role|>user<|end_of_role|>' }}
        {%- endif %}
        {{- '\n<tool_response>\n' }}
        {{- content.val }}
        {{- '\n</tool_response>' }}
        {%- if loop.last or (messages[loop.index0 + 1].role != 'tool') %}
            {{- '<|end_of_text|>\n' }}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
    {{- '<|start_of_role|>assistant<|end_of_role|>' }}
{%- endif %}
```

### 30526 - gemma-4-E2B-it-Q8_0.gguf

配置：
- id `3`：`gemma4-e2b-q8`，type=`normal`，EOS=`<|end_of_text|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `gemma-4-E2B-it-Q8_0.gguf`
- v1 model: `gemma-4-E2B-it-Q8_0.gguf`
- model_path: `/data/models/gemma-4-E2B-it-Q8_0.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=16317 sha256=781d10940fbc44be family=gemma flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=108 sha256=655d3fc903900db0

渲染样例：
```text
<|turn>system
<|think|>
You are a concise assistant.<turn|>
<|turn>user
Answer with OK.<turn|>
<|turn>model
```

完整 chat_template：
```text
{%- macro format_parameters(properties, required) -%}
    {%- set standard_keys = ['description', 'type', 'properties', 'required', 'nullable'] -%}
    {%- set ns = namespace(found_first=false) -%}
    {%- for key, value in properties | dictsort -%}
        {%- set add_comma = false -%}
        {%- if key not in standard_keys -%}
            {%- if ns.found_first %},{% endif -%}
            {%- set ns.found_first = true -%}
            {{ key }}:{
            {%- if value['description'] -%}
                description:<|"|>{{ value['description'] }}<|"|>
                {%- set add_comma = true -%}
            {%- endif -%}
            {%- if value['type'] | upper == 'STRING' -%}
                {%- if value['enum'] -%}
                    {%- if add_comma %},{%- else -%} {%- set add_comma = true -%} {% endif -%}
                    enum:{{ format_argument(value['enum']) }}
                {%- endif -%}
            {%- elif value['type'] | upper == 'ARRAY' -%}
                {%- if value['items'] is mapping and value['items'] -%}
                    {%- if add_comma %},{%- else -%} {%- set add_comma = true -%} {% endif -%}
                    items:{
                    {%- set ns_items = namespace(found_first=false) -%}
                    {%- for item_key, item_value in value['items'] | dictsort -%}
                        {%- if item_value is not none -%}
                            {%- if ns_items.found_first %},{% endif -%}
                            {%- set ns_items.found_first = true -%}
                            {%- if item_key == 'properties' -%}
                                properties:{
                                {%- if item_value is mapping -%}
                                    {{- format_parameters(item_value, value['items']['required'] | default([])) -}}
                                {%- endif -%}
                                }
                            {%- elif item_key == 'required' -%}
                                required:[
                                {%- for req_item in item_value -%}
                                    <|"|>{{- req_item -}}<|"|>
                                    {%- if not loop.last %},{% endif -%}
                                {%- endfor -%}
                                ]
                            {%- elif item_key == 'type' -%}
                                {%- if item_value is string -%}
                                    type:{{ format_argument(item_value | upper) }}
                                {%- else -%}
                                    type:{{ format_argument(item_value | map('upper') | list) }}
                                {%- endif -%}
                            {%- else -%}
                                {{ item_key }}:{{ format_argument(item_value) }}
                            {%- endif -%}
                        {%- endif -%}
                    {%- endfor -%}
                    }
                {%- endif -%}
            {%- endif -%}
            {%- if value['nullable'] %}
                {%- if add_comma %},{%- else -%} {%- set add_comma = true -%} {% endif -%}
                nullable:true
            {%- endif -%}
            {%- if value['type'] | upper == 'OBJECT' -%}
                {%- if value['properties'] is defined and value['properties'] is mapping -%}
                    {%- if add_comma %},{%- else -%} {%- set add_comma = true -%} {% endif -%}
                    properties:{
                    {{- format_parameters(value['properties'], value['required'] | default([])) -}}
                    }
                {%- elif value is mapping -%}
                    {%- if add_comma %},{%- else -%} {%- set add_comma = true -%} {% endif -%}
                    properties:{
                    {{- format_parameters(value, value['required'] | default([])) -}}
                    }
                {%- endif -%}
                {%- if value['required'] -%}
                    {%- if add_comma %},{%- else -%} {%- set add_comma = true -%} {% endif -%}
                    required:[
                    {%- for item in value['required'] | default([]) -%}
                        <|"|>{{- item -}}<|"|>
                        {%- if not loop.last %},{% endif -%}
                    {%- endfor -%}
                    ]
                {%- endif -%}
            {%- endif -%}
            {%- if add_comma %},{%- else -%} {%- set add_comma = true -%} {% endif -%}
            type:<|"|>{{ value['type'] | upper }}<|"|>}
        {%- endif -%}
    {%- endfor -%}
{%- endmacro -%}
{%- macro format_function_declaration(tool_data) -%}
    declaration:{{- tool_data['function']['name'] -}}{description:<|"|>{{- tool_data['function']['description'] -}}<|"|>
    {%- set params = tool_data['function']['parameters'] -%}
    {%- if params -%}
        ,parameters:{
        {%- if params['properties'] -%}
            properties:{ {{- format_parameters(params['properties'], params['required']) -}} },
        {%- endif -%}
        {%- if params['required'] -%}
            required:[
            {%- for item in params['required'] -%}
                <|"|>{{- item -}}<|"|>
                {{- ',' if not loop.last -}}
            {%- endfor -%}
            ],
        {%- endif -%}
        {%- if params['type'] -%}
            type:<|"|>{{- params['type'] | upper -}}<|"|>}
        {%- endif -%}
    {%- endif -%}
    {%- if 'response' in tool_data['function'] -%}
        {%- set response_declaration = tool_data['function']['response'] -%}
        ,response:{
        {%- if response_declaration['description'] -%}
            description:<|"|>{{- response_declaration['description'] -}}<|"|>,
        {%- endif -%}
        {%- if response_declaration['type'] | upper == 'OBJECT' -%}
            type:<|"|>{{- response_declaration['type'] | upper -}}<|"|>}
        {%- endif -%}
    {%- endif -%}
    }
{%- endmacro -%}
{%- macro format_argument(argument, escape_keys=True) -%}
    {%- if argument is string -%}
        {{- '<|"|>' + argument + '<|"|>' -}}
    {%- elif argument is boolean -%}
        {{- 'true' if argument else 'false' -}}
    {%- elif argument is mapping -%}
        {{- '{' -}}
        {%- set ns = namespace(found_first=false) -%}
        {%- for key, value in argument | dictsort -%}
            {%- if ns.found_first %},{% endif -%}
            {%- set ns.found_first = true -%}
            {%- if escape_keys -%}
                {{- '<|"|>' + key + '<|"|>' -}}
            {%- else -%}
                {{- key -}}
            {%- endif -%}
            :{{- format_argument(value, escape_keys=escape_keys) -}}
        {%- endfor -%}
        {{- '}' -}}
    {%- elif argument is sequence -%}
        {{- '[' -}}
        {%- for item in argument -%}
            {{- format_argument(item, escape_keys=escape_keys) -}}
            {%- if not loop.last %},{% endif -%}
        {%- endfor -%}
        {{- ']' -}}
    {%- else -%}
        {{- argument -}}
    {%- endif -%}
{%- endmacro -%}
{%- macro strip_thinking(text) -%}
    {%- set ns = namespace(result='') -%}
    {%- for part in text.split('<channel|>') -%}
        {%- if '<|channel>' in part -%}
            {%- set ns.result = ns.result + part.split('<|channel>')[0] -%}
        {%- else -%}
            {%- set ns.result = ns.result + part -%}
        {%- endif -%}
    {%- endfor -%}
    {{- ns.result | trim -}}
{%- endmacro -%}

{%- macro format_tool_response_block(tool_name, response) -%}
    {{- '<|tool_response>' -}}
    {%- if response is mapping -%}
        {{- 'response:' + tool_name + '{' -}}
        {%- for key, value in response | dictsort -%}
            {{- key -}}:{{- format_argument(value, escape_keys=False) -}}
            {%- if not loop.last %},{% endif -%}
        {%- endfor -%}
        {{- '}' -}}
    {%- else -%}
        {{- 'response:' + tool_name + '{value:' + format_argument(response, escape_keys=False) + '}' -}}
    {%- endif -%}
    {{- '<tool_response|>' -}}
{%- endmacro -%}

{%- set ns = namespace(prev_message_type=None) -%}
{%- set loop_messages = messages -%}
{{- bos_token -}}
{#- Handle System/Tool Definitions Block -#}
{%- if (enable_thinking is defined and enable_thinking) or tools or messages[0]['role'] in ['system', 'developer'] -%}
    {{- '<|turn>system\n' -}}

    {#- Inject Thinking token at the very top of the FIRST system turn -#}
    {%- if enable_thinking is defined and enable_thinking -%}
        {{- '<|think|>\n' -}}
        {%- set ns.prev_message_type = 'think' -%}
    {%- endif -%}

    {%- if messages[0]['role'] in ['system', 'developer'] -%}
        {{- messages[0]['content'] | trim -}}
        {%- set loop_messages = messages[1:] -%}
    {%- endif -%}

    {%- if tools -%}
        {%- for tool in tools %}
            {{- '<|tool>' -}}
            {{- format_function_declaration(tool) | trim -}}
            {{- '<tool|>' -}}
        {%- endfor %}
        {%- set ns.prev_message_type = 'tool' -%}
    {%- endif -%}

    {{- '<turn|>\n' -}}
{%- endif %}

{#- Pre-scan: find last user message index for reasoning guard -#}
{%- set ns_turn = namespace(last_user_idx=-1) -%}
{%- for i in range(loop_messages | length) -%}
    {%- if loop_messages[i]['role'] == 'user' -%}
        {%- set ns_turn.last_user_idx = i -%}
    {%- endif -%}
{%- endfor -%}

{#- Loop through messages -#}
{%- for message in loop_messages -%}
    {%- if message['role'] != 'tool' -%}
    {%- set ns.prev_message_type = None -%}
    {%- set role = 'model' if message['role'] == 'assistant' else message['role'] -%}
    {#- Detect continuation: suppress duplicate <|turn>model when previous non-tool message was also assistant -#}
    {%- set prev_nt = namespace(role=None, found=false) -%}
    {%- if loop.index0 > 0 -%}
        {%- for j in range(loop.index0 - 1, -1, -1) -%}
            {%- if not prev_nt.found -%}
                {%- if loop_messages[j]['role'] != 'tool' -%}
                    {%- set prev_nt.role = loop_messages[j]['role'] -%}
                    {%- set prev_nt.found = true -%}
                {%- endif -%}
            {%- endif -%}
        {%- endfor -%}
    {%- endif -%}
    {%- set continue_same_model_turn = (role == 'model' and prev_nt.role == 'assistant') -%}
    {%- if not continue_same_model_turn -%}
        {{- '<|turn>' + role + '\n' }}
    {%- endif -%}

    {#- Render reasoning/reasoning_content as thinking channel -#}
    {%- set thinking_text = message.get('reasoning') or message.get('reasoning_content') -%}
    {%- if thinking_text and loop.index0 > ns_turn.last_user_idx and message.get('tool_calls') -%}
        {{- '<|channel>thought\n' + thinking_text + '\n<channel|>' -}}
    {%- endif -%}

            {%- if message['tool_calls'] -%}
                {%- for tool_call in message['tool_calls'] -%}
                    {%- set function = tool_call['function'] -%}
                    {{- '<|tool_call>call:' + function['name'] + '{' -}}
                    {%- if function['arguments'] is mapping -%}
                        {%- set ns_args = namespace(found_first=false) -%}
                        {%- for key, value in function['arguments'] | dictsort -%}
                            {%- if ns_args.found_first %},{% endif -%}
                            {%- set ns_args.found_first = true -%}
                            {{- key -}}:{{- format_argument(value, escape_keys=False) -}}
                        {%- endfor -%}
                    {%- elif function['arguments'] is string -%}
                        {{- function['arguments'] -}}
                    {%- endif -%}
                    {{- '}<tool_call|>' -}}
                {%- endfor -%}
                {%- set ns.prev_message_type = 'tool_call' -%}
            {%- endif -%}

            {%- set ns_tr_out = namespace(flag=false) -%}
            {%- if message.get('tool_responses') -%}
                {#- Legacy: tool_responses embedded on the assistant message (Google/Gemma native) -#}
                {%- for tool_response in message['tool_responses'] -%}
                    {{- format_tool_response_block(tool_response['name'] | default('unknown'), tool_response['response']) -}}
                    {%- set ns_tr_out.flag = true -%}
                    {%- set ns.prev_message_type = 'tool_response' -%}
                {%- endfor -%}
            {%- elif message.get('tool_calls') -%}
                {#- OpenAI Chat Completions: forward-scan consecutive role:tool messages -#}
                {%- set ns_tool_scan = namespace(stopped=false) -%}
                {%- for k in range(loop.index0 + 1, loop_messages | length) -%}
                    {%- if ns_tool_scan.stopped -%}
                    {%- elif loop_messages[k]['role'] != 'tool' -%}
                        {%- set ns_tool_scan.stopped = true -%}
                    {%- else -%}
                        {%- set follow = loop_messages[k] -%}
                        {#- Resolve tool_call_id to function name -#}
                        {%- set ns_tname = namespace(name=follow.get('name') | default('unknown')) -%}
                        {%- for tc in message['tool_calls'] -%}
                            {%- if tc.get('id') == follow.get('tool_call_id') -%}
                                {%- set ns_tname.name = tc['function']['name'] -%}
                            {%- endif -%}
                        {%- endfor -%}
                        {#- Handle content as string or content-parts array -#}
                        {%- set tool_body = follow.get('content') -%}
                        {%- if tool_body is string -%}
                            {{- format_tool_response_block(ns_tname.name, tool_body) -}}
                        {%- elif tool_body is sequence and tool_body is not string -%}
                            {%- set ns_txt = namespace(s='') -%}
                            {%- for part in tool_body -%}
                                {%- if part.get('type') == 'text' -%}
                                    {%- set ns_txt.s = ns_txt.s + (part.get('text') | default('')) -%}
                                {%- endif -%}
                            {%- endfor -%}
                            {{- format_tool_response_block(ns_tname.name, ns_txt.s) -}}
                        {%- else -%}
                            {{- format_tool_response_block(ns_tname.name, tool_body) -}}
                        {%- endif -%}
                        {%- set ns_tr_out.flag = true -%}
                        {%- set ns.prev_message_type = 'tool_response' -%}
                    {%- endif -%}
                {%- endfor -%}
            {%- endif -%}

            {%- if message['content'] is string -%}
                {%- if role == 'model' -%}
                    {{- strip_thinking(message['content']) -}}
                {%- else -%}
                    {{- message['content'] | trim -}}
                {%- endif -%}
            {%- elif message['content'] is sequence -%}
                {%- for item in message['content'] -%}
                    {%- if item['type'] == 'text' -%}
                        {%- if role == 'model' -%}
                            {{- strip_thinking(item['text']) -}}
                        {%- else -%}
                            {{- item['text'] | trim -}}
                        {%- endif -%}
                    {%- elif item['type'] == 'image' -%}
                        {{- '<|image|>' -}}
                        {%- set ns.prev_message_type = 'image' -%}
                    {%- elif item['type'] == 'audio' -%}
                        {{- '<|audio|>' -}}
                        {%- set ns.prev_message_type = 'audio' -%}
                    {%- elif item['type'] == 'video' -%}
                        {{- '<|video|>' -}}
                        {%- set ns.prev_message_type = 'video' -%}
                    {%- endif -%}
                {%- endfor -%}
            {%- endif -%}

        {%- if ns.prev_message_type == 'tool_call' and not ns_tr_out.flag -%}
            {{- '<|tool_response>' -}}
        {%- elif not (ns_tr_out.flag and not message.get('content')) -%}
            {{- '<turn|>\n' -}}
        {%- endif -%}
    {%- endif -%}
{%- endfor -%}

{%- if add_generation_prompt -%}
    {%- if ns.prev_message_type != 'tool_response' and ns.prev_message_type != 'tool_call' -%}
        {{- '<|turn>model\n' -}}
    {%- endif -%}
{%- endif -%}
```

### 30528 - gemma-4-E4B-it-UD-Q8_K_XL.gguf

配置：
- id `10`：`gemma4-e4b-q8kxl`，type=`normal`，EOS=`<|end_of_text|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `gemma-4-E4B-it-UD-Q8_K_XL.gguf`
- v1 model: `gemma-4-E4B-it-UD-Q8_K_XL.gguf`
- model_path: `/data/models/gemma-4-E4B-it-UD-Q8_K_XL.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=11926 sha256=55572b8d3c834204 family=gemma flags={'has_system': True, 'has_user': False, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=107 sha256=0b10e4d934663594

渲染样例：
```text
<|turn>system
<|think|>You are a concise assistant.<turn|>
<|turn>user
Answer with OK.<turn|>
<|turn>model
```

完整 chat_template：
```text
{%- macro format_parameters(properties, required) -%}
    {%- set standard_keys = ['description', 'type', 'properties', 'required', 'nullable'] -%}
    {%- set ns = namespace(found_first=false) -%}
    {%- for key, value in properties | dictsort -%}
        {%- set add_comma = false -%}
        {%- if key not in standard_keys -%}
            {%- if ns.found_first %},{% endif -%}
            {%- set ns.found_first = true -%}
            {{ key }}:{
            {%- if value['description'] -%}
                description:<|"|>{{ value['description'] }}<|"|>
                {%- set add_comma = true -%}
            {%- endif -%}
            {%- if value['nullable'] %}
                {%- if add_comma %},{%- else -%} {%- set add_comma = true -%} {% endif -%}
                nullable:true
            {%- endif -%}
            {%- if value['type'] | upper == 'STRING' -%}
                {%- if value['enum'] -%}
                    {%- if add_comma %},{%- else -%} {%- set add_comma = true -%} {% endif -%}
                    enum:{{ format_argument(value['enum']) }}
                {%- endif -%}
            {%- elif value['type'] | upper == 'OBJECT' -%}
                ,properties:{
                {%- if value['properties'] is defined and value['properties'] is mapping -%}
                    {{- format_parameters(value['properties'], value['required'] | default([])) -}}
                {%- elif value is mapping -%}
                    {{- format_parameters(value, value['required'] | default([])) -}}
                {%- endif -%}
                }
                {%- if value['required'] -%}
                    ,required:[
                    {%- for item in value['required'] | default([]) -%}
                        <|"|>{{- item -}}<|"|>
                        {%- if not loop.last %},{% endif -%}
                    {%- endfor -%}
                    ]
                {%- endif -%}
            {%- elif value['type'] | upper == 'ARRAY' -%}
                {%- if value['items'] is mapping and value['items'] -%}
                    ,items:{
                    {%- set ns_items = namespace(found_first=false) -%}
                    {%- for item_key, item_value in value['items'] | dictsort -%}
                        {%- if item_value is not none -%}
                            {%- if ns_items.found_first %},{% endif -%}
                            {%- set ns_items.found_first = true -%}
                            {%- if item_key == 'properties' -%}
                                properties:{
                                {%- if item_value is mapping -%}
                                    {{- format_parameters(item_value, value['items']['required'] | default([])) -}}
                                {%- endif -%}
                                }
                            {%- elif item_key == 'required' -%}
                                required:[
                                {%- for req_item in item_value -%}
                                    <|"|>{{- req_item -}}<|"|>
                                    {%- if not loop.last %},{% endif -%}
                                {%- endfor -%}
                                ]
                            {%- elif item_key == 'type' -%}
                                {%- if item_value is string -%}
                                    type:{{ format_argument(item_value | upper) }}
                                {%- else -%}
                                    type:{{ format_argument(item_value | map('upper') | list) }}
                                {%- endif -%}
                            {%- else -%}
                                {{ item_key }}:{{ format_argument(item_value) }}
                            {%- endif -%}
                        {%- endif -%}
                    {%- endfor -%}
                    }
                {%- endif -%}
            {%- endif -%}
            {%- if add_comma %},{%- else -%} {%- set add_comma = true -%} {% endif -%}
            type:<|"|>{{ value['type'] | upper }}<|"|>}
        {%- endif -%}
    {%- endfor -%}
{%- endmacro -%}
{%- macro format_function_declaration(tool_data) -%}
    declaration:{{- tool_data['function']['name'] -}}{description:<|"|>{{- tool_data['function']['description'] -}}<|"|>
    {%- set params = tool_data['function']['parameters'] -%}
    {%- if params -%}
        ,parameters:{
        {%- if params['properties'] -%}
            properties:{ {{- format_parameters(params['properties'], params['required']) -}} },
        {%- endif -%}
        {%- if params['required'] -%}
            required:[
            {%- for item in params['required'] -%}
                <|"|>{{- item -}}<|"|>
                {{- ',' if not loop.last -}}
            {%- endfor -%}
            ],
        {%- endif -%}
        {%- if params['type'] -%}
            type:<|"|>{{- params['type'] | upper -}}<|"|>}
        {%- endif -%}
    {%- endif -%}
    {%- if 'response' in tool_data['function'] -%}
        {%- set response_declaration = tool_data['function']['response'] -%}
        ,response:{
        {%- if response_declaration['description'] -%}
            description:<|"|>{{- response_declaration['description'] -}}<|"|>,
        {%- endif -%}
        {%- if response_declaration['type'] | upper == 'OBJECT' -%}
            type:<|"|>{{- response_declaration['type'] | upper -}}<|"|>}
        {%- endif -%}
    {%- endif -%}
    }
{%- endmacro -%}
{%- macro format_argument(argument, escape_keys=True) -%}
    {%- if argument is string -%}
        {{- '<|"|>' + argument + '<|"|>' -}}
    {%- elif argument is boolean -%}
        {{- 'true' if argument else 'false' -}}
    {%- elif argument is mapping -%}
        {{- '{' -}}
        {%- set ns = namespace(found_first=false) -%}
        {%- for key, value in argument | dictsort -%}
            {%- if ns.found_first %},{% endif -%}
            {%- set ns.found_first = true -%}
            {%- if escape_keys -%}
                {{- '<|"|>' + key + '<|"|>' -}}
            {%- else -%}
                {{- key -}}
            {%- endif -%}
            :{{- format_argument(value, escape_keys=escape_keys) -}}
        {%- endfor -%}
        {{- '}' -}}
    {%- elif argument is sequence -%}
        {{- '[' -}}
        {%- for item in argument -%}
            {{- format_argument(item, escape_keys=escape_keys) -}}
            {%- if not loop.last %},{% endif -%}
        {%- endfor -%}
        {{- ']' -}}
    {%- else -%}
        {{- argument -}}
    {%- endif -%}
{%- endmacro -%}
{%- macro strip_thinking(text) -%}
    {%- set ns = namespace(result='') -%}
    {%- for part in text.split('<channel|>') -%}
        {%- if '<|channel>' in part -%}
            {%- set ns.result = ns.result + part.split('<|channel>')[0] -%}
        {%- else -%}
            {%- set ns.result = ns.result + part -%}
        {%- endif -%}
    {%- endfor -%}
    {{- ns.result | trim -}}
{%- endmacro -%}

{%- set ns = namespace(prev_message_type=None) -%}
{%- set loop_messages = messages -%}
{{ bos_token }}
{#- Handle System/Tool Definitions Block -#}
{%- if (enable_thinking is defined and enable_thinking) or tools or messages[0]['role'] in ['system', 'developer'] -%}
    {{- '<|turn>system\n' -}}

    {#- Inject Thinking token at the very top of the FIRST system turn -#}
    {%- if enable_thinking is defined and enable_thinking -%}
        {{- '<|think|>' -}}
        {%- set ns.prev_message_type = 'think' -%}
    {%- endif -%}

    {%- if messages[0]['role'] in ['system', 'developer'] -%}
        {{- messages[0]['content'] | trim -}}
        {%- set loop_messages = messages[1:] -%}
    {%- endif -%}

    {%- if tools -%}
        {%- for tool in tools %}
            {{- '<|tool>' -}}
            {{- format_function_declaration(tool) | trim -}}
            {{- '<tool|>' -}}
        {%- endfor %}
        {%- set ns.prev_message_type = 'tool' -%}
    {%- endif -%}

    {{- '<turn|>\n' -}}
{%- endif %}

{#- Loop through messages -#}
{%- for message in loop_messages -%}
    {%- set ns.prev_message_type = None -%}
    {%- set role = 'model' if message['role'] == 'assistant' else message['role'] -%}
        {{- '<|turn>' + role + '\n' }}

            {%- if message['tool_calls'] -%}
                {%- for tool_call in message['tool_calls'] -%}
                    {%- set function = tool_call['function'] -%}
                    {{- '<|tool_call>call:' + function['name'] + '{' -}}
                    {%- if function['arguments'] is mapping -%}
                        {%- set ns_args = namespace(found_first=false) -%}
                        {%- for key, value in function['arguments'] | dictsort -%}
                            {%- if ns_args.found_first %},{% endif -%}
                            {%- set ns_args.found_first = true -%}
                            {{- key -}}:{{- format_argument(value, escape_keys=False) -}}
                        {%- endfor -%}
                    {%- elif function['arguments'] is string -%}
                        {{- function['arguments'] -}}
                    {%- endif -%}
                    {{- '}<tool_call|>' -}}
                {%- endfor -%}
                {%- set ns.prev_message_type = 'tool_call' -%}
            {%- endif -%}

            {%- if message['tool_responses'] -%}
                {#- Tool Response handling -#}
                {%- for tool_response in message['tool_responses'] -%}
                    {{- '<|tool_response>' -}}
                    {%- if tool_response['response'] is mapping -%}
                        {{- 'response:' + tool_response['name'] | default('unknown') + '{' -}}
                        {%- for key, value in tool_response['response'] | dictsort -%}
                            {{- key -}}:{{- format_argument(value, escape_keys=False) -}}
                            {%- if not loop.last %},{% endif -%}
                        {%- endfor -%}
                        {{- '}' -}}
                    {%- else -%}
                        {{- 'response:' + tool_response['name'] | default('unknown') + '{value:' + format_argument(tool_response['response'], escape_keys=False) + '}' -}}
                    {%- endif -%}
                    {{- '<tool_response|>' -}}
                {%- endfor -%}
                {%- set ns.prev_message_type = 'tool_response' -%}
            {%- endif -%}

            {%- if message['content'] is string -%}
                {%- if role == 'model' -%}
                    {{- strip_thinking(message['content']) -}}
                {%- else -%}
                    {{- message['content'] | trim -}}
                {%- endif -%}
            {%- elif message['content'] is sequence -%}
                {%- for item in message['content'] -%}
                    {%- if item['type'] == 'text' -%}
                        {%- if role == 'model' -%}
                            {{- strip_thinking(item['text']) -}}
                        {%- else -%}
                            {{- item['text'] | trim -}}
                        {%- endif -%}
                    {%- elif item['type'] == 'image' -%}
                        {{- '\n\n<|image|>\n\n' -}}
                        {%- set ns.prev_message_type = 'image' -%}
                    {%- elif item['type'] == 'audio' -%}
                        {{- '<|audio|>' -}}
                        {%- set ns.prev_message_type = 'audio' -%}
                    {%- elif item['type'] == 'video' -%}
                        {{- '\n\n<|video|>\n\n' -}}
                        {%- set ns.prev_message_type = 'video' -%}
                    {%- endif -%}
                {%- endfor -%}
            {%- endif -%}

        {%- if not (message['tool_responses'] and not message['content']) -%}
            {{- '<turn|>\n' -}}
        {%- endif -%}
{%- endfor -%}

{%- if add_generation_prompt -%}
    {%- if ns.prev_message_type != 'tool_response' -%}
        {{- '<|turn>model\n' -}}
    {%- endif -%}
{%- endif -%}
```

### 30578 - Qwen3-8B-BF16.gguf

配置：
- id `22`：`qwen3-8b-bf16`，type=`think`，EOS=`<|im_end|>`，stop_think=`</think>`，expose_raw_logits=`False`

- server model_alias: `Qwen3-8B-BF16.gguf`
- v1 model: `Qwen3-8B-BF16.gguf`
- model_path: `/data/models/Qwen3-8B-BF16.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=4905 sha256=5da44855ab7e0641 family=qwen/chatml flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=123 sha256=7a404a07af2cb071

渲染样例：
```text
<|im_start|>system
You are a concise assistant.<|im_end|>
<|im_start|>user
Answer with OK.<|im_end|>
<|im_start|>assistant
```

完整 chat_template：
```text
{%- if tools %}
    {{- '<|im_start|>system\n' }}
    {%- if messages[0].role == 'system' %}
        {{- messages[0].content + '\n\n' }}
    {%- endif %}
    {{- "# Tools\n\nYou may call one or more functions to assist with the user query.\n\nYou are provided with function signatures within <tools></tools> XML tags:\n<tools>" }}
    {%- for tool in tools %}
        {{- "\n" }}
        {{- tool | tojson }}
    {%- endfor %}
    {{- "\n</tools>\n\nFor each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\n<tool_call>\n{\"name\": <function-name>, \"arguments\": <args-json-object>}\n</tool_call><|im_end|>\n" }}
{%- else %}
    {%- if messages[0].role == 'system' %}
        {{- '<|im_start|>system\n' + messages[0].content + '<|im_end|>\n' }}
    {%- endif %}
{%- endif %}
{%- set ns = namespace(multi_step_tool=true, last_query_index=messages|length - 1) %}
{%- for forward_message in messages %}
    {%- set index = (messages|length - 1) - loop.index0 %}
    {%- set message = messages[index] %}
    {%- set current_content = message.content if message.content is defined and message.content is not none else '' %}
    {%- set tool_start = '<tool_response>' %}
    {%- set tool_start_length = tool_start|length %}
    {%- set start_of_message = current_content[:tool_start_length] %}
    {%- set tool_end = '</tool_response>' %}
    {%- set tool_end_length = tool_end|length %}
    {%- set start_pos = (current_content|length) - tool_end_length %}
    {%- if start_pos < 0 %}
        {%- set start_pos = 0 %}
    {%- endif %}
    {%- set end_of_message = current_content[start_pos:] %}
    {%- if ns.multi_step_tool and message.role == "user" and not(start_of_message == tool_start and end_of_message == tool_end) %}
        {%- set ns.multi_step_tool = false %}
        {%- set ns.last_query_index = index %}
    {%- endif %}
{%- endfor %}
{%- for message in messages %}
    {%- if (message.role == "user") or (message.role == "system" and not loop.first) %}
        {{- '<|im_start|>' + message.role + '\n' + message.content + '<|im_end|>' + '\n' }}
    {%- elif message.role == "assistant" %}
        {%- set m_content = message.content if message.content is defined and message.content is not none else '' %}
        {%- set content = m_content %}
        {%- set reasoning_content = '' %}
        {%- if message.reasoning_content is defined and message.reasoning_content is not none %}
            {%- set reasoning_content = message.reasoning_content %}
        {%- else %}
            {%- if '</think>' in m_content %}
                {%- set content = (m_content.split('</think>')|last).lstrip('\n') %}
                {%- set reasoning_content = (m_content.split('</think>')|first).rstrip('\n') %}
                {%- set reasoning_content = (reasoning_content.split('<think>')|last).lstrip('\n') %}
            {%- endif %}
        {%- endif %}
        {%- if loop.index0 > ns.last_query_index %}
            {%- if loop.last or (not loop.last and (not reasoning_content.strip() == '')) %}
                {{- '<|im_start|>' + message.role + '\n<think>\n' + reasoning_content.strip('\n') + '\n</think>\n\n' + content.lstrip('\n') }}
            {%- else %}
                {{- '<|im_start|>' + message.role + '\n' + content }}
            {%- endif %}
        {%- else %}
            {{- '<|im_start|>' + message.role + '\n' + content }}
        {%- endif %}
        {%- if message.tool_calls %}
            {%- for tool_call in message.tool_calls %}
                {%- if (loop.first and content) or (not loop.first) %}
                    {{- '\n' }}
                {%- endif %}
                {%- if tool_call.function %}
                    {%- set tool_call = tool_call.function %}
                {%- endif %}
                {{- '<tool_call>\n{"name": "' }}
                {{- tool_call.name }}
                {{- '", "arguments": ' }}
                {%- if tool_call.arguments is string %}
                    {{- tool_call.arguments }}
                {%- else %}
                    {{- tool_call.arguments | tojson }}
                {%- endif %}
                {{- '}\n</tool_call>' }}
            {%- endfor %}
        {%- endif %}
        {{- '<|im_end|>\n' }}
    {%- elif message.role == "tool" %}
        {%- if loop.first or (messages[loop.index0 - 1].role != "tool") %}
            {{- '<|im_start|>user' }}
        {%- endif %}
        {{- '\n<tool_response>\n' }}
        {{- message.content }}
        {{- '\n</tool_response>' }}
        {%- if loop.last or (messages[loop.index0 + 1].role != "tool") %}
            {{- '<|im_end|>\n' }}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
    {{- '<|im_start|>assistant\n' }}
    {%- if enable_thinking is defined and enable_thinking is false %}
        {{- '<think>\n\n</think>\n\n' }}
    {%- endif %}
{%- endif %}
```

### 30582 - Qwen3-8B-BF16.gguf

配置：
- id `32`：`qwen3-8b-bf16`，type=`think`，EOS=`<|im_end|>`，stop_think=`</think>`，expose_raw_logits=`False`

- server model_alias: `Qwen3-8B-BF16.gguf`
- v1 model: `Qwen3-8B-BF16.gguf`
- model_path: `/data/models/Qwen3-8B-BF16.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=4905 sha256=5da44855ab7e0641 family=qwen/chatml flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=123 sha256=7a404a07af2cb071

渲染样例：
```text
<|im_start|>system
You are a concise assistant.<|im_end|>
<|im_start|>user
Answer with OK.<|im_end|>
<|im_start|>assistant
```

完整 chat_template：
```text
{%- if tools %}
    {{- '<|im_start|>system\n' }}
    {%- if messages[0].role == 'system' %}
        {{- messages[0].content + '\n\n' }}
    {%- endif %}
    {{- "# Tools\n\nYou may call one or more functions to assist with the user query.\n\nYou are provided with function signatures within <tools></tools> XML tags:\n<tools>" }}
    {%- for tool in tools %}
        {{- "\n" }}
        {{- tool | tojson }}
    {%- endfor %}
    {{- "\n</tools>\n\nFor each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\n<tool_call>\n{\"name\": <function-name>, \"arguments\": <args-json-object>}\n</tool_call><|im_end|>\n" }}
{%- else %}
    {%- if messages[0].role == 'system' %}
        {{- '<|im_start|>system\n' + messages[0].content + '<|im_end|>\n' }}
    {%- endif %}
{%- endif %}
{%- set ns = namespace(multi_step_tool=true, last_query_index=messages|length - 1) %}
{%- for forward_message in messages %}
    {%- set index = (messages|length - 1) - loop.index0 %}
    {%- set message = messages[index] %}
    {%- set current_content = message.content if message.content is defined and message.content is not none else '' %}
    {%- set tool_start = '<tool_response>' %}
    {%- set tool_start_length = tool_start|length %}
    {%- set start_of_message = current_content[:tool_start_length] %}
    {%- set tool_end = '</tool_response>' %}
    {%- set tool_end_length = tool_end|length %}
    {%- set start_pos = (current_content|length) - tool_end_length %}
    {%- if start_pos < 0 %}
        {%- set start_pos = 0 %}
    {%- endif %}
    {%- set end_of_message = current_content[start_pos:] %}
    {%- if ns.multi_step_tool and message.role == "user" and not(start_of_message == tool_start and end_of_message == tool_end) %}
        {%- set ns.multi_step_tool = false %}
        {%- set ns.last_query_index = index %}
    {%- endif %}
{%- endfor %}
{%- for message in messages %}
    {%- if (message.role == "user") or (message.role == "system" and not loop.first) %}
        {{- '<|im_start|>' + message.role + '\n' + message.content + '<|im_end|>' + '\n' }}
    {%- elif message.role == "assistant" %}
        {%- set m_content = message.content if message.content is defined and message.content is not none else '' %}
        {%- set content = m_content %}
        {%- set reasoning_content = '' %}
        {%- if message.reasoning_content is defined and message.reasoning_content is not none %}
            {%- set reasoning_content = message.reasoning_content %}
        {%- else %}
            {%- if '</think>' in m_content %}
                {%- set content = (m_content.split('</think>')|last).lstrip('\n') %}
                {%- set reasoning_content = (m_content.split('</think>')|first).rstrip('\n') %}
                {%- set reasoning_content = (reasoning_content.split('<think>')|last).lstrip('\n') %}
            {%- endif %}
        {%- endif %}
        {%- if loop.index0 > ns.last_query_index %}
            {%- if loop.last or (not loop.last and (not reasoning_content.strip() == '')) %}
                {{- '<|im_start|>' + message.role + '\n<think>\n' + reasoning_content.strip('\n') + '\n</think>\n\n' + content.lstrip('\n') }}
            {%- else %}
                {{- '<|im_start|>' + message.role + '\n' + content }}
            {%- endif %}
        {%- else %}
            {{- '<|im_start|>' + message.role + '\n' + content }}
        {%- endif %}
        {%- if message.tool_calls %}
            {%- for tool_call in message.tool_calls %}
                {%- if (loop.first and content) or (not loop.first) %}
                    {{- '\n' }}
                {%- endif %}
                {%- if tool_call.function %}
                    {%- set tool_call = tool_call.function %}
                {%- endif %}
                {{- '<tool_call>\n{"name": "' }}
                {{- tool_call.name }}
                {{- '", "arguments": ' }}
                {%- if tool_call.arguments is string %}
                    {{- tool_call.arguments }}
                {%- else %}
                    {{- tool_call.arguments | tojson }}
                {%- endif %}
                {{- '}\n</tool_call>' }}
            {%- endfor %}
        {%- endif %}
        {{- '<|im_end|>\n' }}
    {%- elif message.role == "tool" %}
        {%- if loop.first or (messages[loop.index0 - 1].role != "tool") %}
            {{- '<|im_start|>user' }}
        {%- endif %}
        {{- '\n<tool_response>\n' }}
        {{- message.content }}
        {{- '\n</tool_response>' }}
        {%- if loop.last or (messages[loop.index0 + 1].role != "tool") %}
            {{- '<|im_end|>\n' }}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
    {{- '<|im_start|>assistant\n' }}
    {%- if enable_thinking is defined and enable_thinking is false %}
        {{- '<think>\n\n</think>\n\n' }}
    {%- endif %}
{%- endif %}
```

### 30584 - Qwen3-4B-Instruct-2507-Q4_K_M.gguf

配置：
- id `14`：`qwen3-4b-instruct-2507-q4km`，type=`normal`，EOS=`<|im_end|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `Qwen3-4B-Instruct-2507-Q4_K_M.gguf`
- v1 model: `Qwen3-4B-Instruct-2507-Q4_K_M.gguf`
- model_path: `/data/models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=4051 sha256=c979e0e71a3e21b8 family=qwen/chatml flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=123 sha256=7a404a07af2cb071

渲染样例：
```text
<|im_start|>system
You are a concise assistant.<|im_end|>
<|im_start|>user
Answer with OK.<|im_end|>
<|im_start|>assistant
```

完整 chat_template：
```text
{%- if tools %}
    {{- '<|im_start|>system\n' }}
    {%- if messages[0].role == 'system' %}
        {{- messages[0].content + '\n\n' }}
    {%- endif %}
    {{- "# Tools\n\nYou may call one or more functions to assist with the user query.\n\nYou are provided with function signatures within <tools></tools> XML tags:\n<tools>" }}
    {%- for tool in tools %}
        {{- "\n" }}
        {{- tool | tojson }}
    {%- endfor %}
    {{- "\n</tools>\n\nFor each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\n<tool_call>\n{\"name\": <function-name>, \"arguments\": <args-json-object>}\n</tool_call><|im_end|>\n" }}
{%- else %}
    {%- if messages[0].role == 'system' %}
        {{- '<|im_start|>system\n' + messages[0].content + '<|im_end|>\n' }}
    {%- endif %}
{%- endif %}
{%- set ns = namespace(multi_step_tool=true, last_query_index=messages|length - 1) %}
{%- for message in messages[::-1] %}
    {%- set index = (messages|length - 1) - loop.index0 %}
    {%- if ns.multi_step_tool and message.role == "user" and message.content is string and not(message.content.startswith('<tool_response>') and message.content.endswith('</tool_response>')) %}
        {%- set ns.multi_step_tool = false %}
        {%- set ns.last_query_index = index %}
    {%- endif %}
{%- endfor %}
{%- for message in messages %}
    {%- if message.content is string %}
        {%- set content = message.content %}
    {%- else %}
        {%- set content = '' %}
    {%- endif %}
    {%- if (message.role == "user") or (message.role == "system" and not loop.first) %}
        {{- '<|im_start|>' + message.role + '\n' + content + '<|im_end|>' + '\n' }}
    {%- elif message.role == "assistant" %}
        {%- set reasoning_content = '' %}
        {%- if message.reasoning_content is string %}
            {%- set reasoning_content = message.reasoning_content %}
        {%- else %}
            {%- if '</think>' in content %}
                {%- set reasoning_content = ((content.split('</think>')|first).rstrip('\n').split('<think>')|last).lstrip('\n') %}
                {%- set content = (content.split('</think>')|last).lstrip('\n') %}
            {%- endif %}
        {%- endif %}
        {%- if loop.index0 > ns.last_query_index %}
            {%- if loop.last or (not loop.last and reasoning_content) %}
                {{- '<|im_start|>' + message.role + '\n<think>\n' + reasoning_content.strip('\n') + '\n</think>\n\n' + content.lstrip('\n') }}
            {%- else %}
                {{- '<|im_start|>' + message.role + '\n' + content }}
            {%- endif %}
        {%- else %}
            {{- '<|im_start|>' + message.role + '\n' + content }}
        {%- endif %}
        {%- if message.tool_calls %}
            {%- for tool_call in message.tool_calls %}
                {%- if (loop.first and content) or (not loop.first) %}
                    {{- '\n' }}
                {%- endif %}
                {%- if tool_call.function %}
                    {%- set tool_call = tool_call.function %}
                {%- endif %}
                {{- '<tool_call>\n{"name": "' }}
                {{- tool_call.name }}
                {{- '", "arguments": ' }}
                {%- if tool_call.arguments is string %}
                    {{- tool_call.arguments }}
                {%- else %}
                    {{- tool_call.arguments | tojson }}
                {%- endif %}
                {{- '}\n</tool_call>' }}
            {%- endfor %}
        {%- endif %}
        {{- '<|im_end|>\n' }}
    {%- elif message.role == "tool" %}
        {%- if loop.first or (messages[loop.index0 - 1].role != "tool") %}
            {{- '<|im_start|>user' }}
        {%- endif %}
        {{- '\n<tool_response>\n' }}
        {{- content }}
        {{- '\n</tool_response>' }}
        {%- if loop.last or (messages[loop.index0 + 1].role != "tool") %}
            {{- '<|im_end|>\n' }}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
    {{- '<|im_start|>assistant\n' }}
{%- endif %}
```

### 30788 - gpt-oss-20b-mxfp4.gguf

配置：
- id `38`：`gpt-oss-20b-mxfp4`，type=`think`，EOS=`<|end|>`，stop_think=`final<|message|>`，expose_raw_logits=`False`

- server model_alias: `gpt-oss-20b-mxfp4.gguf`
- v1 model: `gpt-oss-20b-mxfp4.gguf`
- model_path: `/data/models/gpt-oss-20b-mxfp4.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=14580 sha256=0f1b6cb32273ad2a family=gpt-oss flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=466 sha256=7bb4b3756d07f909

渲染样例：
```text
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2026-05-18

reasoning: medium

# Valid channels: analysis, commentary, final. Channel must be included for every message.
Calls to these tools must go to the commentary channel: 'functions'.<|end|><|start|>developer<|message|># Instructions

You are a concise assistant.<|end|><|start|>user<|message|>Answer with OK.<|end|><|start|>assistant
```

完整 chat_template：
```text
{#-
  In addition to the normal inputs of `messages` and `tools`, this template also accepts the
  following kwargs:
  - "builtin_tools": A list, can contain "browser" and/or "python".
  - "model_identity": A string that optionally describes the model identity.
  - "reasoning_effort": A string that describes the reasoning effort, defaults to "medium".
 #}

{#- Tool Definition Rendering ============================================== #}
{%- macro render_typescript_type(param_spec, required_params, is_nullable=false) -%}
    {%- if param_spec.type == "array" -%}
        {%- if param_spec['items'] -%}
            {%- if param_spec['items']['type'] == "string" -%}
                {{- "string[]" }}
            {%- elif param_spec['items']['type'] == "number" -%}
                {{- "number[]" }}
            {%- elif param_spec['items']['type'] == "integer" -%}
                {{- "number[]" }}
            {%- elif param_spec['items']['type'] == "boolean" -%}
                {{- "boolean[]" }}
            {%- else -%}
                {%- set inner_type = render_typescript_type(param_spec['items'], required_params) -%}
                {%- if inner_type == "object | object" or inner_type|length > 50 -%}
                    {{- "any[]" }}
                {%- else -%}
                    {{- inner_type + "[]" }}
                {%- endif -%}
            {%- endif -%}
            {%- if param_spec.nullable -%}
                {{- " | null" }}
            {%- endif -%}
        {%- else -%}
            {{- "any[]" }}
            {%- if param_spec.nullable -%}
                {{- " | null" }}
            {%- endif -%}
        {%- endif -%}
    {%- elif param_spec.type is defined and param_spec.type is iterable and param_spec.type is not string and param_spec.type is not mapping and param_spec.type[0] is defined -%}
        {#- Handle array of types like ["object", "object"] from Union[dict, list] #}
        {%- if param_spec.type | length > 1 -%}
            {{- param_spec.type | join(" | ") }}
        {%- else -%}
            {{- param_spec.type[0] }}
        {%- endif -%}
    {%- elif param_spec.oneOf -%}
        {#- Handle oneOf schemas - check for complex unions and fallback to any #}
        {%- set has_object_variants = false -%}
        {%- for variant in param_spec.oneOf -%}
            {%- if variant.type == "object" -%}
                {%- set has_object_variants = true -%}
            {%- endif -%}
        {%- endfor -%}
        {%- if has_object_variants and param_spec.oneOf|length > 1 -%}
            {{- "any" }}
        {%- else -%}
            {%- for variant in param_spec.oneOf -%}
                {{- render_typescript_type(variant, required_params) -}}
                {%- if variant.description %}
                    {{- "// " + variant.description }}
                {%- endif -%}
                {%- if variant.default is defined %}
                    {{ "// default: " + variant.default|tojson }}
                {%- endif -%}
                {%- if not loop.last %}
                    {{- " | " }}
                {% endif -%}
            {%- endfor -%}
        {%- endif -%}
    {%- elif param_spec.type == "string" -%}
        {%- if param_spec.enum -%}
            {{- '"' + param_spec.enum|join('" | "') + '"' -}}
        {%- else -%}
            {{- "string" }}
            {%- if param_spec.nullable %}
                {{- " | null" }}
            {%- endif -%}
        {%- endif -%}
    {%- elif param_spec.type == "number" -%}
        {{- "number" }}
    {%- elif param_spec.type == "integer" -%}
        {{- "number" }}
    {%- elif param_spec.type == "boolean" -%}
        {{- "boolean" }}

    {%- elif param_spec.type == "object" -%}
        {%- if param_spec.properties -%}
            {{- "{\n" }}
            {%- for prop_name, prop_spec in param_spec.properties.items() -%}
                {{- prop_name -}}
                {%- if prop_name not in (param_spec.required or []) -%}
                    {{- "?" }}
                {%- endif -%}
                {{- ": " }}
                {{ render_typescript_type(prop_spec, param_spec.required or []) }}
                {%- if not loop.last -%}
                    {{-", " }}
                {%- endif -%}
            {%- endfor -%}
            {{- "}" }}
        {%- else -%}
            {{- "object" }}
        {%- endif -%}
    {%- else -%}
        {{- "any" }}
    {%- endif -%}
{%- endmacro -%}

{%- macro render_tool_namespace(namespace_name, tools) -%}
    {{- "## " + namespace_name + "\n\n" }}
    {{- "namespace " + namespace_name + " {\n\n" }}
    {%- for tool in tools %}
        {%- set tool = tool.function %}
        {{- "// " + tool.description + "\n" }}
        {{- "type "+ tool.name + " = (" }}
        {%- if tool.parameters and tool.parameters.properties -%}
            {{- "_: " }}
            {{- "{\n" }}
            {%- for param_name, param_spec in tool.parameters.properties.items() %}
                {{- "// " + param_spec.description + "\n" }}
                {{- param_name }}
                {%- if param_name not in (tool.parameters.required or []) -%}
                    {{- "?" }}
                {%- endif -%}
                {{- ": " }}
                {{- render_typescript_type(param_spec, tool.parameters.required or []) }}
                {%- if param_spec.default is defined -%}
                    {%- if param_spec.oneOf %}
                        {{- "// default: " + param_spec.default }}
                    {%- else %}
                        {{- ", // default: " + param_spec.default|tojson }}
                    {%- endif -%}
                {%- endif -%}
                {%- if not loop.last %}
                    {{- ",\n" }}
                {%- endif -%}
            {%- endfor %}
            {{- ",\n}) => any;\n" }}
        {%- else -%}
            {{- "\n}) => any;\n" }}
        {%- endif -%}
    {%- endfor %}
    {{- "\n} // namespace " + namespace_name }}
{%- endmacro -%}

{%- macro render_builtin_tools(browser_tool, python_tool) -%}
    {%- if browser_tool %}
        {{- "## browser\n\n" }}
        {{- "// Tool for browsing.\n" }}
        {{- "// The `cursor` appears in brackets before each browsing display: `[{cursor}]`.\n" }}
        {{- "// Cite information from the tool using the following format:\n" }}
        {{- "// `【{cursor}†L{line_start}(-L{line_end})?】`, for example: `【6†L9-L11】` or `【8†L3】`.\n" }}
        {{- "// Do not quote more than 10 words directly from the tool output.\n" }}
        {{- "// sources=web (default: web)\n" }}
        {{- "namespace browser {\n\n" }}
        {{- "// Searches for information related to `query` and displays `topn` results.\n" }}
        {{- "type search = (_: {\n" }}
        {{- "query: string,\n" }}
        {{- "topn?: number, // default: 10\n" }}
        {{- "source?: string,\n" }}
        {{- "}) => any;\n\n" }}
        {{- "// Opens the link `id` from the page indicated by `cursor` starting at line number `loc`, showing `num_lines` lines.\n" }}
        {{- "// Valid link ids are displayed with the formatting: `【{id}†.*】`.\n" }}
        {{- "// If `cursor` is not provided, the most recent page is implied.\n" }}
        {{- "// If `id` is a string, it is treated as a fully qualified URL associated with `source`.\n" }}
        {{- "// If `loc` is not provided, the viewport will be positioned at the beginning of the document or centered on the most relevant passage, if available.\n" }}
        {{- "// Use this function without `id` to scroll to a new location of an opened page.\n" }}
        {{- "type open = (_: {\n" }}
        {{- "id?: number | string, // default: -1\n" }}
        {{- "cursor?: number, // default: -1\n" }}
        {{- "loc?: number, // default: -1\n" }}
        {{- "num_lines?: number, // default: -1\n" }}
        {{- "view_source?: boolean, // default: false\n" }}
        {{- "source?: string,\n" }}
        {{- "}) => any;\n\n" }}
        {{- "// Finds exact matches of `pattern` in the current page, or the page given by `cursor`.\n" }}
        {{- "type find = (_: {\n" }}
        {{- "pattern: string,\n" }}
        {{- "cursor?: number, // default: -1\n" }}
        {{- "}) => any;\n\n" }}
        {{- "} // namespace browser\n\n" }}
    {%- endif -%}

    {%- if python_tool %}
        {{- "## python\n\n" }}
        {{- "Use this tool to execute Python code in your chain of thought. The code will not be shown to the user. This tool should be used for internal reasoning, but not for code that is intended to be visible to the user (e.g. when creating plots, tables, or files).\n\n" }}
        {{- "When you send a message containing Python code to python, it will be executed in a stateful Jupyter notebook environment. python will respond with the output of the execution or time out after 120.0 seconds. The drive at '/mnt/data' can be used to save and persist user files. Internet access for this session is UNKNOWN. Depends on the cluster.\n\n" }}
    {%- endif -%}
{%- endmacro -%}

{#- System Message Construction ============================================ #}
{%- macro build_system_message() -%}
    {%- if model_identity is not defined %}
        {{- "You are ChatGPT, a large language model trained by OpenAI.\n" -}}
    {%- else %}
        {{- model_identity }}
    {%- endif %}
    {{- "Knowledge cutoff: 2024-06\n" }}
    {{- "Current date: " + strftime_now("%Y-%m-%d") + "\n\n" }}
    {%- if reasoning_effort is not defined %}
        {%- set reasoning_effort = "medium" %}
    {%- endif %}
    {{- "reasoning: " + reasoning_effort + "\n\n" }}
    {%- if builtin_tools %}
        {{- "# Tools\n\n" }}
        {%- set available_builtin_tools = namespace(browser=false, python=false) %}
        {%- for tool in builtin_tools %}
            {%- if tool == "browser" %}
                {%- set available_builtin_tools.browser = true %}
            {%- elif tool == "python" %}
                {%- set available_builtin_tools.python = true %}
            {%- endif %}
        {%- endfor %}
        {{- render_builtin_tools(available_builtin_tools.browser, available_builtin_tools.python) }}
    {%- endif -%}
    {{- "# Valid channels: analysis, commentary, final. Channel must be included for every message.\n" }}
    {{- "Calls to these tools must go to the commentary channel: 'functions'." }}
{%- endmacro -%}

{#- Main Template Logic ================================================= #}
{#- Set defaults #}

{#- Render system message #}
{{- "<|start|>system<|message|>" }}
{{- build_system_message() }}
{{- "<|end|>" }}

{#- Extract developer message #}
{%- if messages[0].role == "developer" or messages[0].role == "system" %}
    {%- set developer_message = messages[0].content %}
    {%- set loop_messages = messages[1:] %}
{%- else %}
    {%- set developer_message = "" %}
    {%- set loop_messages = messages %}
{%- endif %}

{#- Render developer message #}
{%- if developer_message or tools %}
    {{- "<|start|>developer<|message|>" }}
    {%- if developer_message %}
        {{- "# Instructions\n\n" }}
        {{- developer_message }}
    {%- endif %}
    {%- if tools -%}
        {{- "\n\n" }}
        {{- "# Tools\n\n" }}
        {{- render_tool_namespace("functions", tools) }}
    {%- endif -%}
    {{- "<|end|>" }}
{%- endif %}

{#- Render messages #}
{%- set last_tool_call = namespace(name=none) %}
{%- for message in loop_messages -%}
    {#- At this point only assistant/user/tool messages should remain #}
    {%- if message.role == 'assistant' -%}
        {%- if "tool_calls" in message %}
            {#- We assume max 1 tool call per message, and so we infer the tool call name #}
            {#- in "tool" messages from the most recent assistant tool call name #}
            {%- set tool_call = message.tool_calls[0] %}
            {%- if tool_call.function %}
                {%- set tool_call = tool_call.function %}
            {%- endif %}
            {%- if message.content %}
                {{- "<|start|>assistant<|channel|>analysis<|message|>" + message.content + "<|end|>" }}
            {%- endif %}
            {{- "<|start|>assistant to=" }}
            {{- "functions." + tool_call.name + "<|channel|>commentary json<|message|>" }}
            {{- tool_call.arguments|tojson }}
            {{- "<|end|>" }}
            {%- set last_tool_call.name = tool_call.name %}
        {%- elif "thinking" in message and loop.last and not add_generation_prompt %}
            {#- Only render the CoT if the final turn is an assistant turn and add_generation_prompt is false #}
            {#- This is a situation that should only occur in training, never in inference. #}
            {{- "<|start|>assistant<|channel|>analysis<|message|>" + message.thinking + "<|end|>" }}
            {#- <|return|> indicates the end of generation, but <|end|> does not #}
            {#- <|return|> should never be an input to the model, but we include it as the final token #}
            {#- when training, so the model learns to emit it. #}
            {{- "<|start|>assistant<|channel|>final<|message|>" + message.content + "<|return|>" }}
            {%- set last_tool_call.name = none %}
        {%- elif "thinking" in message %}
            {#- CoT is dropped during all previous turns, so we never render it for inference #}
            {{- "<|start|>assistant<|channel|>final<|message|>" + message.content + "<|end|>" }}
            {%- set last_tool_call.name = none %}
        {%- elif loop.last and not add_generation_prompt %}
            {#- <|return|> indicates the end of generation, but <|end|> does not #}
            {#- <|return|> should never be an input to the model, but we include it as the final token #}
            {#- when training, so the model learns to emit it. #}
            {{- "<|start|>assistant<|message|>" + message.content + "<|return|>" }}
        {%- else %}
            {{- "<|start|>assistant<|message|>" + message.content + "<|end|>" }}
            {%- set last_tool_call.name = none %}
        {%- endif %}
    {%- elif message.role == 'tool' -%}
        {%- if last_tool_call.name is none %}
            {{- raise_exception("Message has tool role, but there was no previous assistant message with a tool call!") }}
        {%- endif %}
        {{- "<|start|>functions." + last_tool_call.name }}
        {{- " to=assistant<|channel|>commentary<|message|>" + message.content|tojson + "<|end|>" }}
    {%- else -%}
        {{- "<|start|>user<|message|>" + message.content + "<|end|>" }}
    {%- endif -%}
{%- endfor -%}

{#- Generation prompt #}
{%- if add_generation_prompt -%}
<|start|>assistant
{%- endif -%}
```

### 30834 - Llama-3.1-8B-Instruct-Q8_0.gguf

配置：
- id `2`：`meta-llama-31-8b-instruct-q80`，type=`normal`，EOS=`<|end_of_text|>`，stop_think=`<|None|>`，expose_raw_logits=`True`

- server model_alias: `Llama-3.1-8B-Instruct-Q8_0.gguf`
- v1 model: `Llama-3.1-8B-Instruct-Q8_0.gguf`
- model_path: `/data/models/Llama-3.1-8B-Instruct-Q8_0.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=4613 sha256=93c0e9aa3629bbd7 family=llama-3 flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=289 sha256=8df0c197e1667aae

渲染样例：
```text
<|start_header_id|>system<|end_header_id|>

Environment: ipython
Tools: 

Cutting Knowledge Date: December 2023
Today Date: 18 May 2026

You are a concise assistant.<|eot_id|><|start_header_id|>user<|end_header_id|>

Answer with OK.<|eot_id|><|start_header_id|>assistant<|end_header_id|>
```

完整 chat_template：
```text
{{- bos_token }}
{%- if custom_tools is defined %}
    {%- set tools = custom_tools %}
{%- endif %}
{%- if not tools_in_user_message is defined %}
    {%- set tools_in_user_message = true %}
{%- endif %}
{%- if not date_string is defined %}
    {%- set date_string = "26 Jul 2024" %}
{%- endif %}
{%- if not tools is defined %}
    {%- set tools = none %}
{%- endif %}

{#- This block extracts the system message, so we can slot it into the right place. #}
{%- if messages[0]['role'] == 'system' %}
    {%- set system_message = messages[0]['content']|trim %}
    {%- set messages = messages[1:] %}
{%- else %}
    {%- set system_message = "" %}
{%- endif %}

{#- System message + builtin tools #}
{{- "<|start_header_id|>system<|end_header_id|>\n\n" }}
{%- if builtin_tools is defined or tools is not none %}
    {{- "Environment: ipython\n" }}
{%- endif %}
{%- if builtin_tools is defined %}
    {{- "Tools: " + builtin_tools | reject('equalto', 'code_interpreter') | join(", ") + "\n\n"}}
{%- endif %}
{{- "Cutting Knowledge Date: December 2023\n" }}
{{- "Today Date: " + date_string + "\n\n" }}
{%- if tools is not none and not tools_in_user_message %}
    {{- "You have access to the following functions. To call a function, please respond with JSON for a function call." }}
    {{- 'Respond in the format {"name": function name, "parameters": dictionary of argument name and its value}.' }}
    {{- "Do not use variables.\n\n" }}
    {%- for t in tools %}
        {{- t | tojson(indent=4) }}
        {{- "\n\n" }}
    {%- endfor %}
{%- endif %}
{{- system_message }}
{{- "<|eot_id|>" }}

{#- Custom tools are passed in a user message with some extra guidance #}
{%- if tools_in_user_message and not tools is none %}
    {#- Extract the first user message so we can plug it in here #}
    {%- if messages | length != 0 %}
        {%- set first_user_message = messages[0]['content']|trim %}
        {%- set messages = messages[1:] %}
    {%- else %}
        {{- raise_exception("Cannot put tools in the first user message when there's no first user message!") }}
{%- endif %}
    {{- '<|start_header_id|>user<|end_header_id|>\n\n' -}}
    {{- "Given the following functions, please respond with a JSON for a function call " }}
    {{- "with its proper arguments that best answers the given prompt.\n\n" }}
    {{- 'Respond in the format {"name": function name, "parameters": dictionary of argument name and its value}.' }}
    {{- "Do not use variables.\n\n" }}
    {%- for t in tools %}
        {{- t | tojson(indent=4) }}
        {{- "\n\n" }}
    {%- endfor %}
    {{- first_user_message + "<|eot_id|>"}}
{%- endif %}

{%- for message in messages %}
    {%- if not (message.role == 'ipython' or message.role == 'tool' or 'tool_calls' in message) %}
        {{- '<|start_header_id|>' + message['role'] + '<|end_header_id|>\n\n'+ message['content'] | trim + '<|eot_id|>' }}
    {%- elif 'tool_calls' in message %}
        {%- if not message.tool_calls|length == 1 %}
            {{- raise_exception("This model only supports single tool-calls at once!") }}
        {%- endif %}
        {%- set tool_call = message.tool_calls[0].function %}
        {%- if builtin_tools is defined and tool_call.name in builtin_tools %}
            {{- '<|start_header_id|>assistant<|end_header_id|>\n\n' -}}
            {{- "<|python_tag|>" + tool_call.name + ".call(" }}
            {%- for arg_name, arg_val in tool_call.arguments | items %}
                {{- arg_name + '="' + arg_val + '"' }}
                {%- if not loop.last %}
                    {{- ", " }}
                {%- endif %}
                {%- endfor %}
            {{- ")" }}
        {%- else  %}
            {{- '<|start_header_id|>assistant<|end_header_id|>\n\n' -}}
            {{- '{"name": "' + tool_call.name + '", ' }}
            {{- '"parameters": ' }}
            {{- tool_call.arguments | tojson }}
            {{- "}" }}
        {%- endif %}
        {%- if builtin_tools is defined %}
            {#- This means we're in ipython mode #}
            {{- "<|eom_id|>" }}
        {%- else %}
            {{- "<|eot_id|>" }}
        {%- endif %}
    {%- elif message.role == "tool" or message.role == "ipython" %}
        {{- "<|start_header_id|>ipython<|end_header_id|>\n\n" }}
        {%- if message.content is mapping or message.content is iterable %}
            {{- message.content | tojson }}
        {%- else %}
            {{- message.content }}
        {%- endif %}
        {{- "<|eot_id|>" }}
    {%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
    {{- '<|start_header_id|>assistant<|end_header_id|>\n\n' }}
{%- endif %}
```

### 30905 - tencent_Hunyuan-7B-Instruct-Q5_K_M.gguf

配置：
- id `8`：`hunyuan-7b-instruct-q5km`，type=`normal`，EOS=`<|eos|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `tencent_Hunyuan-7B-Instruct-Q5_K_M.gguf`
- v1 model: `tencent_Hunyuan-7B-Instruct-Q5_K_M.gguf`
- model_path: `/data/models/tencent_Hunyuan-7B-Instruct-Q5_K_M.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=4919 sha256=7dfb19355e3c8779 family=hunyuan flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=98 sha256=b9cd8f391c23d070

渲染样例：
```text
<|startoftext|>You are a concise assistant.<|extra_4|>Answer with OK.<|extra_0|><think>

</think>
```

完整 chat_template：
```text
{%- if not add_generation_prompt is defined %}
    {%- set add_generation_prompt = false %}
{%- endif %}
{%- set ns = namespace(is_first=false, is_tool=false, is_output_first=true, system_prompt='', is_first_sp=true, is_first_user=true, is_last_user=false) %}
{%- for message in messages %}
    {%- if message['role'] == 'system' %}
        {%- if ns.is_first_sp %}
            {%- set ns.system_prompt = ns.system_prompt + message['content'] %}
            {%- set ns.is_first_sp = false %}
        {%- else %}
            {%- set ns.system_prompt = ns.system_prompt + '

' + message['content'] %}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{{- bos_token }}
{{- ns.system_prompt }}
{%- if tools %}
    {%- if ns.system_prompt != '' %}
        {{- '

# Tools

You may call one or more functions to assist with the user query.' }}
    {%- else %}
        {{- '# Tools

You may call one or more functions to assist with the user query.' }}
    {%- endif %}
    {{- '

You are provided with function signatures within <tools></tools> XML tags:' }}
    {{- '
<tools>
' }}
    {%- for tool in tools %}
        {%- if loop.index0 > 0 %}
            {{- '
' }}
        {%- endif %}
        {{- tool | tojson }}
    {%- endfor %}
    {{- '
</tools>

' }}
    {{- 'For function call returns, you should first print <tool_calls>' }}
    {{- 'For each function call, you should return object like:
' }}
    {{- '<tool_call>function_name
` ` `json
function_arguments_in_json_format
` ` `</tool_call>' }}
    {{- 'At the end of function call returns, you should print </tool_calls>' }}
{%- endif %}
{%- if ns.system_prompt != '' or tools %}
    {{- '<|extra_4|>' }}
{%- endif %}
{%- for message in messages %}
    {%- if message['role'] == 'user' %}
        {%- set ns.is_tool = false %}
        {%- set ns.is_first = false %}
        {%- set ns.is_last_user = true %}
        {%- if ns.is_first_user %}
            {{- message['content'] + '<|extra_0|>' }}
            {%- set ns.is_first_user = false %}
        {%- else %}
            {{- bos_token + message['content'] + '<|extra_0|>' }}
        {%- endif %}
    {%- endif %}
    {%- if message['role'] == 'assistant' and message['tool_calls'] is defined and message['tool_calls'] is not none %}
        {%- set ns.is_last_user = false %}
        {%- if ns.is_tool %}
            {{- '</tool_responses>' + '<|extra_0|>' }}
        {%- endif %}
        {%- set ns.is_first = false %}
        {%- set ns.is_tool = false %}
        {%- set ns.is_output_first = true %}
        {%- for tool in message['tool_calls'] %}
            {%- set arguments = tool['function']['arguments'] %}
            {%- if arguments is not string %}
                {%- set arguments = arguments | tojson %}
            {%- endif %}
            {%- if not ns.is_first %}
                {%- if message['content'] is none %}
                    {{- '<tool_calls><tool_call>' + tool['function']['name'] + '
' + '` ` `json' + '
' + arguments + '
' + '` ` `' + '</tool_call>' }}
                {%- else %}
                    {{- message['content'] + '<tool_calls><tool_call>' + tool['function']['name'] + '
' + '` ` `json' + '
' + arguments + '
' + '` ` `' + '</tool_call>' }}
                {%- endif %}
            {%- set ns.is_first = true %}
            {%- else %}
                {{- '
' + '<tool_call>' + tool['function']['name'] + '
' + '` ` `json' + '
' + arguments + '
' + '` ` `' + '</tool_call>' }}
            {%- endif %}
        {%- endfor %}
        {{- '</tool_calls>' + eos_token }}
    {%- endif %}
    {%- if message['role'] == 'assistant' and (message['tool_calls'] is not defined or message['tool_calls'] is none) %}
        {%- set content = message['content'] %}
        {%- if '<answer>' in content and not loop.last %}
            {%- set content = content.split('<answer>')[-1].strip('</answer>').strip() %}
        {%- endif %}
        {%- set ns.is_last_user = false %}
        {%- if ns.is_tool %}
            {{- '</tool_responses>' + '<|extra_0|>' + content + eos_token }}
            {%- set ns.is_tool = false %}
        {%- else %}
            {{- content + eos_token }}
        {%- endif %}
    {%- endif %}
    {%- if message['role'] == 'tool' %}
        {%- set ns.is_last_user = false %}
        {%- set ns.is_tool = true %}
        {%- if ns.is_output_first %}
            {{- bos_token + '<tool_responses><tool_response>' + message['content'] + '</tool_response>' }}
            {%- set ns.is_output_first = false %}
        {%- else %}
            {{- '
<tool_response>' + message['content'] + '</tool_response>' }}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{%- if ns.is_tool %}
    {{- '</tool_responses>' + '<|extra_0|>' }}
{%- endif %}
{%- if add_generation_prompt and not ns.is_last_user and not ns.is_tool %}
    {{- '<|extra_0|>' }}
{%- endif %}
{%- if enable_thinking is defined and not enable_thinking %}
    {{- '<think>

</think>
' }}
{%- endif %}
```

### 30920 - gemma-3-27b-it-Q4_K_M.gguf

配置：
- id `34`：`gemma-3-27b-it-q4`，type=`normal`，EOS=`<|end_of_text|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `gemma-3-27b-it-Q4_K_M.gguf`
- v1 model: `gemma-3-27b-it-Q4_K_M.gguf`
- model_path: `/data/models/gemma-3-27b-it-Q4_K_M.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=1532 sha256=7de1c58e208eda46 family=gemma flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=100 sha256=45d43bb6ff1ddd31

渲染样例：
```text
<start_of_turn>user
You are a concise assistant.

Answer with OK.<end_of_turn>
<start_of_turn>model
```

完整 chat_template：
```text
{{ bos_token }}
{%- if messages[0]['role'] == 'system' -%}
    {%- if messages[0]['content'] is string -%}
        {%- set first_user_prefix = messages[0]['content'] + '

' -%}
    {%- else -%}
        {%- set first_user_prefix = messages[0]['content'][0]['text'] + '

' -%}
    {%- endif -%}
    {%- set loop_messages = messages[1:] -%}
{%- else -%}
    {%- set first_user_prefix = "" -%}
    {%- set loop_messages = messages -%}
{%- endif -%}
{%- for message in loop_messages -%}
    {%- if (message['role'] == 'user') != (loop.index0 % 2 == 0) -%}
        {{ raise_exception("Conversation roles must alternate user/assistant/user/assistant/...") }}
    {%- endif -%}
    {%- if (message['role'] == 'assistant') -%}
        {%- set role = "model" -%}
    {%- else -%}
        {%- set role = message['role'] -%}
    {%- endif -%}
    {{ '<start_of_turn>' + role + '
' + (first_user_prefix if loop.first else "") }}
    {%- if message['content'] is string -%}
        {{ message['content'] | trim }}
    {%- elif message['content'] is iterable -%}
        {%- for item in message['content'] -%}
            {%- if item['type'] == 'image' -%}
                {{ '<start_of_image>' }}
            {%- elif item['type'] == 'text' -%}
                {{ item['text'] | trim }}
            {%- endif -%}
        {%- endfor -%}
    {%- else -%}
        {{ raise_exception("Invalid content type") }}
    {%- endif -%}
    {{ '<end_of_turn>
' }}
{%- endfor -%}
{%- if add_generation_prompt -%}
    {{'<start_of_turn>model
'}}
{%- endif -%}

```

### 30926 - Qwen3.5-9B-UD-Q8_K_XL.gguf

配置：
- id `33`：`qwen35-9b-q8kxl`，type=`think`，EOS=`<|endoftext|>`，stop_think=`</think>`，expose_raw_logits=`False`

- server model_alias: `Qwen3.5-9B-UD-Q8_K_XL.gguf`
- v1 model: `Qwen3.5-9B-UD-Q8_K_XL.gguf`
- model_path: `/data/models/Qwen3.5-9B-UD-Q8_K_XL.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=7816 sha256=7f0e529032c25183 family=qwen/chatml flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=131 sha256=eccfed9a9c4a2fa4

渲染样例：
```text
<|im_start|>system
You are a concise assistant.<|im_end|>
<|im_start|>user
Answer with OK.<|im_end|>
<|im_start|>assistant
<think>
```

完整 chat_template：
```text
{%- set image_count = namespace(value=0) %}
{%- set video_count = namespace(value=0) %}
{%- macro render_content(content, do_vision_count, is_system_content=false) %}
    {%- if content is string %}
        {{- content }}
    {%- elif content is iterable and content is not mapping %}
        {%- for item in content %}
            {%- if 'image' in item or 'image_url' in item or item.type == 'image' %}
                {%- if is_system_content %}
                    {{- raise_exception('System message cannot contain images.') }}
                {%- endif %}
                {%- if do_vision_count %}
                    {%- set image_count.value = image_count.value + 1 %}
                {%- endif %}
                {%- if add_vision_id %}
                    {{- 'Picture ' ~ image_count.value ~ ': ' }}
                {%- endif %}
                {{- '<|vision_start|><|image_pad|><|vision_end|>' }}
            {%- elif 'video' in item or item.type == 'video' %}
                {%- if is_system_content %}
                    {{- raise_exception('System message cannot contain videos.') }}
                {%- endif %}
                {%- if do_vision_count %}
                    {%- set video_count.value = video_count.value + 1 %}
                {%- endif %}
                {%- if add_vision_id %}
                    {{- 'Video ' ~ video_count.value ~ ': ' }}
                {%- endif %}
                {{- '<|vision_start|><|video_pad|><|vision_end|>' }}
            {%- elif 'text' in item %}
                {{- item.text }}
            {%- else %}
                {{- raise_exception('Unexpected item type in content.') }}
            {%- endif %}
        {%- endfor %}
    {%- elif content is none or content is undefined %}
        {{- '' }}
    {%- else %}
        {{- raise_exception('Unexpected content type.') }}
    {%- endif %}
{%- endmacro %}
{%- if not messages %}
    {{- raise_exception('No messages provided.') }}
{%- endif %}
{%- if tools and tools is iterable and tools is not mapping %}
    {{- '<|im_start|>system\n' }}
    {{- "# Tools\n\nYou have access to the following functions:\n\n<tools>" }}
    {%- for tool in tools %}
        {{- "\n" }}
        {{- tool | tojson }}
    {%- endfor %}
    {{- "\n</tools>" }}
    {{- '\n\nIf you choose to call a function ONLY reply in the following format with NO suffix:\n\n<tool_call>\n<function=example_function_name>\n<parameter=example_parameter_1>\nvalue_1\n</parameter>\n<parameter=example_parameter_2>\nThis is the value for the second parameter\nthat can span\nmultiple lines\n</parameter>\n</function>\n</tool_call>\n\n<IMPORTANT>\nReminder:\n- Function calls MUST follow the specified format: an inner <function=...></function> block must be nested within <tool_call></tool_call> XML tags\n- Required parameters MUST be specified\n- You may provide optional reasoning for your function call in natural language BEFORE the function call, but NOT after\n- If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls\n</IMPORTANT>' }}
    {%- if messages[0].role == 'system' %}
        {%- set content = render_content(messages[0].content, false, true)|trim %}
        {%- if content %}
            {{- '\n\n' + content }}
        {%- endif %}
    {%- endif %}
    {{- '<|im_end|>\n' }}
{%- else %}
    {%- if messages[0].role == 'system' %}
        {%- set content = render_content(messages[0].content, false, true)|trim %}
        {{- '<|im_start|>system\n' + content + '<|im_end|>\n' }}
    {%- endif %}
{%- endif %}
{%- set ns = namespace(multi_step_tool=true, last_query_index=messages|length - 1) %}
{%- for message in messages[::-1] %}
    {%- set index = (messages|length - 1) - loop.index0 %}
    {%- if ns.multi_step_tool and message.role == "user" %}
        {%- set content = render_content(message.content, false)|trim %}
        {%- if not(content.startswith('<tool_response>') and content.endswith('</tool_response>')) %}
            {%- set ns.multi_step_tool = false %}
            {%- set ns.last_query_index = index %}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{%- if ns.multi_step_tool %}
    {{- raise_exception('No user query found in messages.') }}
{%- endif %}
{%- for message in messages %}
    {%- set content = render_content(message.content, true)|trim %}
    {%- if message.role == "system" %}
        {%- if not loop.first %}
            {{- raise_exception('System message must be at the beginning.') }}
        {%- endif %}
    {%- elif message.role == "user" %}
        {{- '<|im_start|>' + message.role + '\n' + content + '<|im_end|>' + '\n' }}
    {%- elif message.role == "assistant" %}
        {%- set reasoning_content = '' %}
        {%- if message.reasoning_content is string %}
            {%- set reasoning_content = message.reasoning_content %}
        {%- else %}
            {%- if '</think>' in content %}
                {%- set reasoning_content = content.split('</think>')[0].rstrip('\n').split('<think>')[-1].lstrip('\n') %}
                {%- set content = content.split('</think>')[-1].lstrip('\n') %}
            {%- endif %}
        {%- endif %}
        {%- set reasoning_content = reasoning_content|trim %}
        {%- if loop.index0 > ns.last_query_index %}
            {{- '<|im_start|>' + message.role + '\n<think>\n' + reasoning_content + '\n</think>\n\n' + content }}
        {%- else %}
            {{- '<|im_start|>' + message.role + '\n' + content }}
        {%- endif %}
        {%- if message.tool_calls and message.tool_calls is iterable and message.tool_calls is not mapping %}
            {%- for tool_call in message.tool_calls %}
                {%- if tool_call.function is defined %}
                    {%- set tool_call = tool_call.function %}
                {%- endif %}
                {%- if loop.first %}
                    {%- if content|trim %}
                        {{- '\n\n<tool_call>\n<function=' + tool_call.name + '>\n' }}
                    {%- else %}
                        {{- '<tool_call>\n<function=' + tool_call.name + '>\n' }}
                    {%- endif %}
                {%- else %}
                    {{- '\n<tool_call>\n<function=' + tool_call.name + '>\n' }}
                {%- endif %}
                {%- if tool_call.arguments is mapping %}
                    {%- for args_name in tool_call.arguments %}
                        {%- set args_value = tool_call.arguments[args_name] %}
                        {{- '<parameter=' + args_name + '>\n' }}
                        {%- set args_value = args_value | tojson | safe if args_value is mapping or (args_value is sequence and args_value is not string) else args_value | string %}
                        {{- args_value }}
                        {{- '\n</parameter>\n' }}
                    {%- endfor %}
                {%- endif %}
                {{- '</function>\n</tool_call>' }}
            {%- endfor %}
        {%- endif %}
        {{- '<|im_end|>\n' }}
    {%- elif message.role == "tool" %}
        {%- if loop.previtem and loop.previtem.role != "tool" %}
            {{- '<|im_start|>user' }}
        {%- endif %}
        {{- '\n<tool_response>\n' }}
        {{- content }}
        {{- '\n</tool_response>' }}
        {%- if not loop.last and loop.nextitem.role != "tool" %}
            {{- '<|im_end|>\n' }}
        {%- elif loop.last %}
            {{- '<|im_end|>\n' }}
        {%- endif %}
    {%- else %}
        {{- raise_exception('Unexpected message role.') }}
    {%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
    {{- '<|im_start|>assistant\n' }}
    {%- if enable_thinking is defined and enable_thinking is true %}
        {{- '<think>\n' }}
    {%- else %}
        {{- '<think>\n\n</think>\n\n' }}
    {%- endif %}
{%- endif %}
```

### 30927 - Qwen3.5-9B-UD-Q8_K_XL.gguf

配置：
- id `39`：`qwen35-9b-q8kxl`，type=`think`，EOS=`<|im_end|>`，stop_think=`</think>`，expose_raw_logits=`False`

- server model_alias: `Qwen3.5-9B-UD-Q8_K_XL.gguf`
- v1 model: `Qwen3.5-9B-UD-Q8_K_XL.gguf`
- model_path: `/data/models/Qwen3.5-9B-UD-Q8_K_XL.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=7816 sha256=7f0e529032c25183 family=qwen/chatml flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=131 sha256=eccfed9a9c4a2fa4

渲染样例：
```text
<|im_start|>system
You are a concise assistant.<|im_end|>
<|im_start|>user
Answer with OK.<|im_end|>
<|im_start|>assistant
<think>
```

完整 chat_template：
```text
{%- set image_count = namespace(value=0) %}
{%- set video_count = namespace(value=0) %}
{%- macro render_content(content, do_vision_count, is_system_content=false) %}
    {%- if content is string %}
        {{- content }}
    {%- elif content is iterable and content is not mapping %}
        {%- for item in content %}
            {%- if 'image' in item or 'image_url' in item or item.type == 'image' %}
                {%- if is_system_content %}
                    {{- raise_exception('System message cannot contain images.') }}
                {%- endif %}
                {%- if do_vision_count %}
                    {%- set image_count.value = image_count.value + 1 %}
                {%- endif %}
                {%- if add_vision_id %}
                    {{- 'Picture ' ~ image_count.value ~ ': ' }}
                {%- endif %}
                {{- '<|vision_start|><|image_pad|><|vision_end|>' }}
            {%- elif 'video' in item or item.type == 'video' %}
                {%- if is_system_content %}
                    {{- raise_exception('System message cannot contain videos.') }}
                {%- endif %}
                {%- if do_vision_count %}
                    {%- set video_count.value = video_count.value + 1 %}
                {%- endif %}
                {%- if add_vision_id %}
                    {{- 'Video ' ~ video_count.value ~ ': ' }}
                {%- endif %}
                {{- '<|vision_start|><|video_pad|><|vision_end|>' }}
            {%- elif 'text' in item %}
                {{- item.text }}
            {%- else %}
                {{- raise_exception('Unexpected item type in content.') }}
            {%- endif %}
        {%- endfor %}
    {%- elif content is none or content is undefined %}
        {{- '' }}
    {%- else %}
        {{- raise_exception('Unexpected content type.') }}
    {%- endif %}
{%- endmacro %}
{%- if not messages %}
    {{- raise_exception('No messages provided.') }}
{%- endif %}
{%- if tools and tools is iterable and tools is not mapping %}
    {{- '<|im_start|>system\n' }}
    {{- "# Tools\n\nYou have access to the following functions:\n\n<tools>" }}
    {%- for tool in tools %}
        {{- "\n" }}
        {{- tool | tojson }}
    {%- endfor %}
    {{- "\n</tools>" }}
    {{- '\n\nIf you choose to call a function ONLY reply in the following format with NO suffix:\n\n<tool_call>\n<function=example_function_name>\n<parameter=example_parameter_1>\nvalue_1\n</parameter>\n<parameter=example_parameter_2>\nThis is the value for the second parameter\nthat can span\nmultiple lines\n</parameter>\n</function>\n</tool_call>\n\n<IMPORTANT>\nReminder:\n- Function calls MUST follow the specified format: an inner <function=...></function> block must be nested within <tool_call></tool_call> XML tags\n- Required parameters MUST be specified\n- You may provide optional reasoning for your function call in natural language BEFORE the function call, but NOT after\n- If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls\n</IMPORTANT>' }}
    {%- if messages[0].role == 'system' %}
        {%- set content = render_content(messages[0].content, false, true)|trim %}
        {%- if content %}
            {{- '\n\n' + content }}
        {%- endif %}
    {%- endif %}
    {{- '<|im_end|>\n' }}
{%- else %}
    {%- if messages[0].role == 'system' %}
        {%- set content = render_content(messages[0].content, false, true)|trim %}
        {{- '<|im_start|>system\n' + content + '<|im_end|>\n' }}
    {%- endif %}
{%- endif %}
{%- set ns = namespace(multi_step_tool=true, last_query_index=messages|length - 1) %}
{%- for message in messages[::-1] %}
    {%- set index = (messages|length - 1) - loop.index0 %}
    {%- if ns.multi_step_tool and message.role == "user" %}
        {%- set content = render_content(message.content, false)|trim %}
        {%- if not(content.startswith('<tool_response>') and content.endswith('</tool_response>')) %}
            {%- set ns.multi_step_tool = false %}
            {%- set ns.last_query_index = index %}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{%- if ns.multi_step_tool %}
    {{- raise_exception('No user query found in messages.') }}
{%- endif %}
{%- for message in messages %}
    {%- set content = render_content(message.content, true)|trim %}
    {%- if message.role == "system" %}
        {%- if not loop.first %}
            {{- raise_exception('System message must be at the beginning.') }}
        {%- endif %}
    {%- elif message.role == "user" %}
        {{- '<|im_start|>' + message.role + '\n' + content + '<|im_end|>' + '\n' }}
    {%- elif message.role == "assistant" %}
        {%- set reasoning_content = '' %}
        {%- if message.reasoning_content is string %}
            {%- set reasoning_content = message.reasoning_content %}
        {%- else %}
            {%- if '</think>' in content %}
                {%- set reasoning_content = content.split('</think>')[0].rstrip('\n').split('<think>')[-1].lstrip('\n') %}
                {%- set content = content.split('</think>')[-1].lstrip('\n') %}
            {%- endif %}
        {%- endif %}
        {%- set reasoning_content = reasoning_content|trim %}
        {%- if loop.index0 > ns.last_query_index %}
            {{- '<|im_start|>' + message.role + '\n<think>\n' + reasoning_content + '\n</think>\n\n' + content }}
        {%- else %}
            {{- '<|im_start|>' + message.role + '\n' + content }}
        {%- endif %}
        {%- if message.tool_calls and message.tool_calls is iterable and message.tool_calls is not mapping %}
            {%- for tool_call in message.tool_calls %}
                {%- if tool_call.function is defined %}
                    {%- set tool_call = tool_call.function %}
                {%- endif %}
                {%- if loop.first %}
                    {%- if content|trim %}
                        {{- '\n\n<tool_call>\n<function=' + tool_call.name + '>\n' }}
                    {%- else %}
                        {{- '<tool_call>\n<function=' + tool_call.name + '>\n' }}
                    {%- endif %}
                {%- else %}
                    {{- '\n<tool_call>\n<function=' + tool_call.name + '>\n' }}
                {%- endif %}
                {%- if tool_call.arguments is mapping %}
                    {%- for args_name in tool_call.arguments %}
                        {%- set args_value = tool_call.arguments[args_name] %}
                        {{- '<parameter=' + args_name + '>\n' }}
                        {%- set args_value = args_value | tojson | safe if args_value is mapping or (args_value is sequence and args_value is not string) else args_value | string %}
                        {{- args_value }}
                        {{- '\n</parameter>\n' }}
                    {%- endfor %}
                {%- endif %}
                {{- '</function>\n</tool_call>' }}
            {%- endfor %}
        {%- endif %}
        {{- '<|im_end|>\n' }}
    {%- elif message.role == "tool" %}
        {%- if loop.previtem and loop.previtem.role != "tool" %}
            {{- '<|im_start|>user' }}
        {%- endif %}
        {{- '\n<tool_response>\n' }}
        {{- content }}
        {{- '\n</tool_response>' }}
        {%- if not loop.last and loop.nextitem.role != "tool" %}
            {{- '<|im_end|>\n' }}
        {%- elif loop.last %}
            {{- '<|im_end|>\n' }}
        {%- endif %}
    {%- else %}
        {{- raise_exception('Unexpected message role.') }}
    {%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
    {{- '<|im_start|>assistant\n' }}
    {%- if enable_thinking is defined and enable_thinking is true %}
        {{- '<think>\n' }}
    {%- else %}
        {{- '<think>\n\n</think>\n\n' }}
    {%- endif %}
{%- endif %}
```

### 31021 - glm-4-9b-chat.Q4_K.gguf

配置：
- id `6`：`glm-4-9b-chat-q4k`，type=`normal`，EOS=`<|endoftext|>`，stop_think=`<|None|>`，expose_raw_logits=`True`

- server model_alias: `glm-4-9b-chat.Q4_K.gguf`
- v1 model: `glm-4-9b-chat.Q4_K.gguf`
- model_path: `/data/models/glm-4-9b-chat.Q4_K.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=544 sha256=fbd6f678a56640d9 family=glm flags={'has_system': True, 'has_user': False, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=89 sha256=08a99427e6cb9c0c

渲染样例：
```text
[gMASK]<sop><|system|>
You are a concise assistant.<|user|>
Answer with OK.<|assistant|>
```

完整 chat_template：
```text
[gMASK]<sop>{% for item in messages %}{% if item['tools'] is defined %}<|system|>
你是一个名为 ChatGLM 的人工智能助手。你是基于智谱AI训练的语言模型 GLM-4 模型开发的，你的任务是针对用户的问题和要求提供适当的答复和支持。

# 可用工具 {% set tools = item['tools'] %}{% for tool in tools %}{% if tool['type'] == 'function' %}

## {{ tool['function']['name'] }}

{{ tool['function'] | tojson(indent=4) }}
......{% endif %}{% endfor %}{% endif %}{% if item['content'] %}<|{{ item['role'] }}|>{{ item['metadata'] }}
{{ item['content'] }}{% endif %}{% endfor %}{% if add_generation_prompt %}<|assistant|>
{% endif %}
```

### 31329 - Kimi-VL-A3B-Instruct.Q4_K_M.gguf

配置：
- id `19`：`kimi-vl-a3b-instruct-q4km`，type=`normal`，EOS=`<|im_end|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `Kimi-VL-A3B-Instruct.Q4_K_M.gguf`
- v1 model: `Kimi-VL-A3B-Instruct.Q4_K_M.gguf`
- model_path: `/data/models/Kimi-VL-A3B-Instruct.Q4_K_M.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=907 sha256=8452948e3156f904 family=kimi flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=161 sha256=6f264cec2b359859

渲染样例：
```text
<|im_system|>system<|im_middle|>You are a concise assistant.<|im_end|><|im_user|>user<|im_middle|>Answer with OK.<|im_end|><|im_assistant|>assistant<|im_middle|>
```

完整 chat_template：
```text
{%- for message in messages -%}{%- if loop.first and messages[0]['role'] != 'system' -%}{{'<|im_system|>system<|im_middle|>You are a helpful assistant<|im_end|>'}}{%- endif -%}{%- if message['role'] == 'system' -%}{{'<|im_system|>'}}{%- endif -%}{%- if message['role'] == 'user' -%}{{'<|im_user|>'}}{%- endif -%}{%- if message['role'] == 'assistant' -%}{{'<|im_assistant|>'}}{%- endif -%}{{- message['role'] -}}{{'<|im_middle|>'}}{%- if message['content'] is string -%}{{- message['content'] + '<|im_end|>' -}}{%- else -%}{%- for content in message['content'] -%}{%- if content['type'] == 'image' or 'image' in content or 'image_url' in content -%}{{'<|media_start|>image<|media_content|><|media_pad|><|media_end|>'}}{%- else -%}{{content['text']}}{%- endif -%}{%- endfor -%}{{'<|im_end|>'}}{%- endif -%}{%- endfor -%}{%- if add_generation_prompt -%}{{'<|im_assistant|>assistant<|im_middle|>'}}{%- endif -%}
```

### 31466 - glm-4-9b-chat.Q4_K.gguf

配置：
- id `13`：`glm-4-9b-chat-q4k`，type=`normal`，EOS=`<|endoftext|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `glm-4-9b-chat.Q4_K.gguf`
- v1 model: `glm-4-9b-chat.Q4_K.gguf`
- model_path: `/data/models/glm-4-9b-chat.Q4_K.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=544 sha256=fbd6f678a56640d9 family=glm flags={'has_system': True, 'has_user': False, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=89 sha256=08a99427e6cb9c0c

渲染样例：
```text
[gMASK]<sop><|system|>
You are a concise assistant.<|user|>
Answer with OK.<|assistant|>
```

完整 chat_template：
```text
[gMASK]<sop>{% for item in messages %}{% if item['tools'] is defined %}<|system|>
你是一个名为 ChatGLM 的人工智能助手。你是基于智谱AI训练的语言模型 GLM-4 模型开发的，你的任务是针对用户的问题和要求提供适当的答复和支持。

# 可用工具 {% set tools = item['tools'] %}{% for tool in tools %}{% if tool['type'] == 'function' %}

## {{ tool['function']['name'] }}

{{ tool['function'] | tojson(indent=4) }}
......{% endif %}{% endfor %}{% endif %}{% if item['content'] %}<|{{ item['role'] }}|>{{ item['metadata'] }}
{{ item['content'] }}{% endif %}{% endfor %}{% if add_generation_prompt %}<|assistant|>
{% endif %}
```

### 31541 - qwen2.5-7b-instruct-q5_k_m.gguf

配置：
- id `21`：`qwen25-7b-instruct-q5km`，type=`normal`，EOS=`<|im_end|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `qwen2.5-7b-instruct-q5_k_m.gguf`
- v1 model: `qwen2.5-7b-instruct-q5_k_m.gguf`
- model_path: `/data/models/qwen2.5-7b-instruct-q5_k_m.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=2509 sha256=d5495a1e5db06111 family=qwen/chatml flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=123 sha256=7a404a07af2cb071

渲染样例：
```text
<|im_start|>system
You are a concise assistant.<|im_end|>
<|im_start|>user
Answer with OK.<|im_end|>
<|im_start|>assistant
```

完整 chat_template：
```text
{%- if tools %}
    {{- '<|im_start|>system\n' }}
    {%- if messages[0]['role'] == 'system' %}
        {{- messages[0]['content'] }}
    {%- else %}
        {{- 'You are Qwen, created by Alibaba Cloud. You are a helpful assistant.' }}
    {%- endif %}
    {{- "\n\n# Tools\n\nYou may call one or more functions to assist with the user query.\n\nYou are provided with function signatures within <tools></tools> XML tags:\n<tools>" }}
    {%- for tool in tools %}
        {{- "\n" }}
        {{- tool | tojson }}
    {%- endfor %}
    {{- "\n</tools>\n\nFor each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\n<tool_call>\n{{\"name\": <function-name>, \"arguments\": <args-json-object>}}\n</tool_call><|im_end|>\n" }}
{%- else %}
    {%- if messages[0]['role'] == 'system' %}
        {{- '<|im_start|>system\n' + messages[0]['content'] + '<|im_end|>\n' }}
    {%- else %}
        {{- '<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n' }}
    {%- endif %}
{%- endif %}
{%- for message in messages %}
    {%- if (message.role == "user") or (message.role == "system" and not loop.first) or (message.role == "assistant" and not message.tool_calls) %}
        {{- '<|im_start|>' + message.role + '\n' + message.content + '<|im_end|>' + '\n' }}
    {%- elif message.role == "assistant" %}
        {{- '<|im_start|>' + message.role }}
        {%- if message.content %}
            {{- '\n' + message.content }}
        {%- endif %}
        {%- for tool_call in message.tool_calls %}
            {%- if tool_call.function is defined %}
                {%- set tool_call = tool_call.function %}
            {%- endif %}
            {{- '\n<tool_call>\n{"name": "' }}
            {{- tool_call.name }}
            {{- '", "arguments": ' }}
            {{- tool_call.arguments | tojson }}
            {{- '}\n</tool_call>' }}
        {%- endfor %}
        {{- '<|im_end|>\n' }}
    {%- elif message.role == "tool" %}
        {%- if (loop.index0 == 0) or (messages[loop.index0 - 1].role != "tool") %}
            {{- '<|im_start|>user' }}
        {%- endif %}
        {{- '\n<tool_response>\n' }}
        {{- message.content }}
        {{- '\n</tool_response>' }}
        {%- if loop.last or (messages[loop.index0 + 1].role != "tool") %}
            {{- '<|im_end|>\n' }}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
    {{- '<|im_start|>assistant\n' }}
{%- endif %}

```

### 32246 - qwen2.5-7b-instruct-q5_k_m.gguf

配置：
- id `5`：`qwen25-7b-instruct-q5km`，type=`normal`，EOS=`<|im_end|>`，stop_think=`<|None|>`，expose_raw_logits=`True`

- server model_alias: `qwen2.5-7b-instruct-q5_k_m.gguf`
- v1 model: `qwen2.5-7b-instruct-q5_k_m.gguf`
- model_path: `/data/models/qwen2.5-7b-instruct-q5_k_m.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=2508 sha256=4e9918361c284a93 family=qwen/chatml flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=123 sha256=7a404a07af2cb071

渲染样例：
```text
<|im_start|>system
You are a concise assistant.<|im_end|>
<|im_start|>user
Answer with OK.<|im_end|>
<|im_start|>assistant
```

完整 chat_template：
```text
{%- if tools %}
    {{- '<|im_start|>system\n' }}
    {%- if messages[0]['role'] == 'system' %}
        {{- messages[0]['content'] }}
    {%- else %}
        {{- 'You are Qwen, created by Alibaba Cloud. You are a helpful assistant.' }}
    {%- endif %}
    {{- "\n\n# Tools\n\nYou may call one or more functions to assist with the user query.\n\nYou are provided with function signatures within <tools></tools> XML tags:\n<tools>" }}
    {%- for tool in tools %}
        {{- "\n" }}
        {{- tool | tojson }}
    {%- endfor %}
    {{- "\n</tools>\n\nFor each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\n<tool_call>\n{{\"name\": <function-name>, \"arguments\": <args-json-object>}}\n</tool_call><|im_end|>\n" }}
{%- else %}
    {%- if messages[0]['role'] == 'system' %}
        {{- '<|im_start|>system\n' + messages[0]['content'] + '<|im_end|>\n' }}
    {%- else %}
        {{- '<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n' }}
    {%- endif %}
{%- endif %}
{%- for message in messages %}
    {%- if (message.role == "user") or (message.role == "system" and not loop.first) or (message.role == "assistant" and not message.tool_calls) %}
        {{- '<|im_start|>' + message.role + '\n' + message.content + '<|im_end|>' + '\n' }}
    {%- elif message.role == "assistant" %}
        {{- '<|im_start|>' + message.role }}
        {%- if message.content %}
            {{- '\n' + message.content }}
        {%- endif %}
        {%- for tool_call in message.tool_calls %}
            {%- if tool_call.function is defined %}
                {%- set tool_call = tool_call.function %}
            {%- endif %}
            {{- '\n<tool_call>\n{"name": "' }}
            {{- tool_call.name }}
            {{- '", "arguments": ' }}
            {{- tool_call.arguments | tojson }}
            {{- '}\n</tool_call>' }}
        {%- endfor %}
        {{- '<|im_end|>\n' }}
    {%- elif message.role == "tool" %}
        {%- if (loop.index0 == 0) or (messages[loop.index0 - 1].role != "tool") %}
            {{- '<|im_start|>user' }}
        {%- endif %}
        {{- '\n<tool_response>\n' }}
        {{- message.content }}
        {{- '\n</tool_response>' }}
        {%- if loop.last or (messages[loop.index0 + 1].role != "tool") %}
            {{- '<|im_end|>\n' }}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
    {{- '<|im_start|>assistant\n' }}
{%- endif %}
```

### 32685 - Llama-3.1-8B-Instruct-Q8_0.gguf

配置：
- id `7`：`meta-llama-31-8b-instruct-q80`，type=`normal`，EOS=`<|end_of_text|>`，stop_think=`<|None|>`，expose_raw_logits=`False`

- server model_alias: `Llama-3.1-8B-Instruct-Q8_0.gguf`
- v1 model: `Llama-3.1-8B-Instruct-Q8_0.gguf`
- model_path: `/data/models/Llama-3.1-8B-Instruct-Q8_0.gguf`
- chat_format: `Content-only`; reasoning_format: `none`; generation_prompt: ``
- chat_template: len=4613 sha256=93c0e9aa3629bbd7 family=llama-3 flags={'has_system': True, 'has_user': True, 'has_assistant': True, 'has_generation_prompt': True}
- apply-template: ok len=289 sha256=8df0c197e1667aae

渲染样例：
```text
<|start_header_id|>system<|end_header_id|>

Environment: ipython
Tools: 

Cutting Knowledge Date: December 2023
Today Date: 18 May 2026

You are a concise assistant.<|eot_id|><|start_header_id|>user<|end_header_id|>

Answer with OK.<|eot_id|><|start_header_id|>assistant<|end_header_id|>
```

完整 chat_template：
```text
{{- bos_token }}
{%- if custom_tools is defined %}
    {%- set tools = custom_tools %}
{%- endif %}
{%- if not tools_in_user_message is defined %}
    {%- set tools_in_user_message = true %}
{%- endif %}
{%- if not date_string is defined %}
    {%- set date_string = "26 Jul 2024" %}
{%- endif %}
{%- if not tools is defined %}
    {%- set tools = none %}
{%- endif %}

{#- This block extracts the system message, so we can slot it into the right place. #}
{%- if messages[0]['role'] == 'system' %}
    {%- set system_message = messages[0]['content']|trim %}
    {%- set messages = messages[1:] %}
{%- else %}
    {%- set system_message = "" %}
{%- endif %}

{#- System message + builtin tools #}
{{- "<|start_header_id|>system<|end_header_id|>\n\n" }}
{%- if builtin_tools is defined or tools is not none %}
    {{- "Environment: ipython\n" }}
{%- endif %}
{%- if builtin_tools is defined %}
    {{- "Tools: " + builtin_tools | reject('equalto', 'code_interpreter') | join(", ") + "\n\n"}}
{%- endif %}
{{- "Cutting Knowledge Date: December 2023\n" }}
{{- "Today Date: " + date_string + "\n\n" }}
{%- if tools is not none and not tools_in_user_message %}
    {{- "You have access to the following functions. To call a function, please respond with JSON for a function call." }}
    {{- 'Respond in the format {"name": function name, "parameters": dictionary of argument name and its value}.' }}
    {{- "Do not use variables.\n\n" }}
    {%- for t in tools %}
        {{- t | tojson(indent=4) }}
        {{- "\n\n" }}
    {%- endfor %}
{%- endif %}
{{- system_message }}
{{- "<|eot_id|>" }}

{#- Custom tools are passed in a user message with some extra guidance #}
{%- if tools_in_user_message and not tools is none %}
    {#- Extract the first user message so we can plug it in here #}
    {%- if messages | length != 0 %}
        {%- set first_user_message = messages[0]['content']|trim %}
        {%- set messages = messages[1:] %}
    {%- else %}
        {{- raise_exception("Cannot put tools in the first user message when there's no first user message!") }}
{%- endif %}
    {{- '<|start_header_id|>user<|end_header_id|>\n\n' -}}
    {{- "Given the following functions, please respond with a JSON for a function call " }}
    {{- "with its proper arguments that best answers the given prompt.\n\n" }}
    {{- 'Respond in the format {"name": function name, "parameters": dictionary of argument name and its value}.' }}
    {{- "Do not use variables.\n\n" }}
    {%- for t in tools %}
        {{- t | tojson(indent=4) }}
        {{- "\n\n" }}
    {%- endfor %}
    {{- first_user_message + "<|eot_id|>"}}
{%- endif %}

{%- for message in messages %}
    {%- if not (message.role == 'ipython' or message.role == 'tool' or 'tool_calls' in message) %}
        {{- '<|start_header_id|>' + message['role'] + '<|end_header_id|>\n\n'+ message['content'] | trim + '<|eot_id|>' }}
    {%- elif 'tool_calls' in message %}
        {%- if not message.tool_calls|length == 1 %}
            {{- raise_exception("This model only supports single tool-calls at once!") }}
        {%- endif %}
        {%- set tool_call = message.tool_calls[0].function %}
        {%- if builtin_tools is defined and tool_call.name in builtin_tools %}
            {{- '<|start_header_id|>assistant<|end_header_id|>\n\n' -}}
            {{- "<|python_tag|>" + tool_call.name + ".call(" }}
            {%- for arg_name, arg_val in tool_call.arguments | items %}
                {{- arg_name + '="' + arg_val + '"' }}
                {%- if not loop.last %}
                    {{- ", " }}
                {%- endif %}
                {%- endfor %}
            {{- ")" }}
        {%- else  %}
            {{- '<|start_header_id|>assistant<|end_header_id|>\n\n' -}}
            {{- '{"name": "' + tool_call.name + '", ' }}
            {{- '"parameters": ' }}
            {{- tool_call.arguments | tojson }}
            {{- "}" }}
        {%- endif %}
        {%- if builtin_tools is defined %}
            {#- This means we're in ipython mode #}
            {{- "<|eom_id|>" }}
        {%- else %}
            {{- "<|eot_id|>" }}
        {%- endif %}
    {%- elif message.role == "tool" or message.role == "ipython" %}
        {{- "<|start_header_id|>ipython<|end_header_id|>\n\n" }}
        {%- if message.content is mapping or message.content is iterable %}
            {{- message.content | tojson }}
        {%- else %}
            {{- message.content }}
        {%- endif %}
        {{- "<|eot_id|>" }}
    {%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
    {{- '<|start_header_id|>assistant<|end_header_id|>\n\n' }}
{%- endif %}
```
