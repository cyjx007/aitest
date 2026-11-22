# aitest

[![test](https://github.com/cyjx007/aitest/actions/workflows/test.yml/badge.svg)](https://github.com/cyjx007/aitest/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**零第三方依赖的 AI 提示词与模型回归测试工具。**

[English](README.md) · 中文

`aitest` 读取一份 JSON 测试用例，把 `input` 交给模型适配器，对返回文本做确定性断言，
最后在终端或 JSON 报告里给出通过情况。核心只使用 Python 标准库，因此可以直接放进 CI，
不需要安装任何厂商 SDK。

项目故意做得很小：内置的通用 JSON-over-HTTP 适配器覆盖简单服务；厂商相关逻辑应放在
实现 `ModelAdapter` 协议的适配器里。目前还没有内置 OpenAI、Anthropic 或本地模型集成。

## 功能

- **JSON 用例**：`id`、`input`，以及可选的包含/排除/精确匹配断言。
- **可插拔适配器**：只有一个方法 `generate(prompt) -> str`。
- **内置 HTTP 适配器**：POST `{"prompt": ...}`，接受返回 JSON 中的 `output` 或 `text`。
- **Echo 适配器**：原样返回提示词，用于冒烟测试。
- **两种输出**：逐条 PASS/FAIL，或 `--json` 机器可读报告。
- **正确的退出码**：全部通过返回 `0`，否则返回 `1`。

## 依赖

- Python 3.10 或更新版本。
- 运行时无第三方依赖。

## 安装

```bash
git clone https://github.com/cyjx007/aitest.git
cd aitest
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
aitest --help
```

Windows 下激活虚拟环境用 `.venv\Scripts\activate`。

## 快速开始

用 Echo 适配器跑自带的冒烟用例：

```bash
aitest examples/smoke.json
```

输出类似：

```text
[PASS] echo-1
[PASS] echo-2

2/2 passed
```

输出机器可读报告：

```bash
aitest examples/smoke.json --json
```

不想安装时，可以直接从工作区运行：

```bash
PYTHONPATH=src python -m aitest examples/smoke.json
```

## 用例格式

测试文件是一个 JSON 数组。每条用例必须有 `id` 和 `input`，断言可选：

```json
[
  {
    "id": "greeting",
    "input": "Say hello",
    "expected_contains": ["hello"],
    "expected_not_contains": ["error"]
  },
  {
    "id": "exact-answer",
    "input": "What is 6 times 7?",
    "exact": "42"
  }
]
```

| 字段 | 必填 | 含义 |
| --- | --- | --- |
| `id` | 是 | 报告里显示的用例名。 |
| `input` | 是 | 传给适配器的提示词。 |
| `expected_contains` | 否 | 输出中必须出现的子串。 |
| `expected_not_contains` | 否 | 输出中不能出现的子串。 |
| `exact` | 否 | 输出必须完全等于该字符串。 |

`expected_contains` / `expected_not_contains` 是不区分大小写的子串检查；`exact` 是
区分大小写的全串比较。所有写出的断言都必须通过；没有任何断言的用例只验证适配器没有抛错。

## 模型适配器

### Echo 适配器

不传 `--url` 时使用 Echo 适配器。它原样返回提示词，只适合检查工具链和测试文件本身。

### HTTP 适配器

内置适配器发送 JSON 请求并读取 JSON 响应：

```text
POST <url>
Content-Type: application/json

{"prompt": "..."}
```

响应必须是 JSON 对象，并带有字符串字段 `output` 或 `text`：

```json
{"output": "hello"}
```

用法：

```bash
aitest examples/http-model.json --url http://127.0.0.1:8000/generate
aitest examples/http-model.json --url http://127.0.0.1:8000/generate --timeout 60
```

`--timeout` 单位为秒，默认 30。适配器不带认证头；需要认证时，在前面放一个反向代理，
或者自己实现适配器。

### 自定义适配器

实现 `generate()` 后传给 `Evaluator`：

```python
from aitest import Case, Evaluator


class MyAdapter:
    def generate(self, prompt: str) -> str:
        return call_my_model(prompt)


results = Evaluator(MyAdapter()).run([
    Case(id="greeting", input="Say hello", expected_contains=["hello"]),
])

for result in results:
    print(result.case_id, result.passed, result.failures)
```

## 命令行参数

```text
aitest [FILE] [--json] [--url URL] [--timeout SECONDS]
```

| 参数 | 说明 |
| --- | --- |
| `FILE` | JSON 用例文件。省略时打印帮助并返回 `0`。 |
| `--json` | 输出结构化报告，而不是 PASS/FAIL 行。 |
| `--url URL` | 使用 JSON-over-HTTP 适配器，而不是 Echo。 |
| `--timeout N` | HTTP 超时秒数，默认 `30`。 |

人类可读报告会为每条用例打印一行 `[PASS]` 或 `[FAIL]`，随后列出失败原因和
`通过数/总数`。JSON 报告结构如下：

```json
{
  "passed": false,
  "total": 2,
  "passed_count": 1,
  "failed_count": 1,
  "results": [
    {
      "case_id": "greeting",
      "passed": true,
      "output": "hello",
      "failures": []
    }
  ]
}
```

如果适配器抛错（例如 HTTP 端点不可达），本次运行会直接异常退出，不会生成部分报告。

## 目录结构

```text
src/aitest/
  core.py      Case、ModelAdapter、Evaluator、EvaluationResult
  model.py     JSON-over-HTTP 适配器
  report.py    报告聚合与 JSON 序列化
  cli.py       argparse 入口（含 Echo 适配器）
  __main__.py  支持 `python -m aitest`
examples/      smoke.json、http-model.json
tests/         使用假适配器的 unittest 测试
```

## 开发与测试

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
PYTHONPATH=src python -m aitest examples/smoke.json
```

测试使用假适配器，不会调用真实模型。CI 在 Python 3.10 到 3.13 上运行。

## 限制

- 请求是同步、串行的，没有并发或重试。
- 不统计延迟、token 或成本。
- HTTP 适配器只支持一种请求/响应格式，且不支持认证。
- 测试文件是静态 JSON，没有数据集模板或矩阵展开。
- 断言是确定性文本检查，不是模型评分。

## 许可证

[MIT](LICENSE)。
