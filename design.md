# Design Document - LLM-Based Black-Box Testing Tool

## 1. Goal and Scope

This tool provides a lightweight framework for black-box testing using an LLM. It accepts:
- (1) requirement text, or
- (2) testing codebase/module context (docs/snippets)

and generates test artifacts using selectable black-box techniques:
- Equivalence Partitioning (EP) + Boundary Value Analysis (BVA)
- Decision Table Testing
- State Transition Testing model generator
- Testing combinations of inputs (pairwise-focused)

The focus is on tool architecture, prompt iteration, and experimental analysis (coverage/accuracy/generalizability), not full end-to-end test execution.

## 2. Key Decisions

- UI: Minimal, single-page web form for input and JSON output display.
- Architecture: Monolith (no strict front-end/back-end separation).
- Stack: FastAPI + Jinja2 + OpenAI API.
- Output: Structured JSON for downstream processing.

## 3. System Architecture

- Web UI (Jinja2): Simple form for requirement input and codebase context input.
- API (FastAPI): Endpoints that call the LLM and return structured JSON.
- Prompt Manager: Versioned prompt templates (V1-V4) plus specialized multi-step prompts for EP/BVA and Decision Table.
- Streaming: Server-Sent Events (SSE) support for real-time output streaming.
- Logging: Store request metadata (model, temperature, prompt version, time).

## 4. Functional Requirements

- FR-1: Accept requirement text OR codebase/module context as input.
- FR-2: Generate structured JSON output.
- FR-3: Support EP+BVA at minimum; optionally support decision table / state transition / combinatorial.
- FR-4: Support prompt versioning and iteration notes.
- FR-5: Provide a minimal UI to validate the API.

## 5. Non-Functional Requirements

- NFR-1: Fast response for small to medium requirements.
- NFR-2: Deterministic output where possible (low temperature).
- NFR-3: Clear error handling and retries for API failures.

## 6. API Design

### POST /api/generate

Request JSON:
{
  "requirements": "...",
  "code_context": "...",
  "input_type": "requirements",
  "technique": "ep_bva",
  "prompt_version": "v1",
  "model": "gpt-4o-mini",
  "temperature": 0.2
}

Response JSON:
{
  "input_variables": ["..."],
  "equivalence_partitions": [
    {
      "id": "EP1",
      "description": "...",
      "valid": true
    }
  ],
  "boundary_values": [
    {
      "variable": "...",
      "values": ["...", "...", "..."]
    }
  ],
  "test_cases": [
    {
      "id": "TC1",
      "scenario": "...",
      "inputs": {
        "var1": "..."
      },
      "expected": "..."
    }
  ],
  "meta": {
    "input_type": "requirements",
    "technique": "ep_bva",
    "prompt_version": "v4",
    "model": "gpt-4o-mini",
    "temperature": 0.2
  },
  "notes": "..."
}

## 7. Prompt Strategy

- V1: Extract variables + EP + BVA + test cases.
- V2: Force JSON schema and explicit valid/invalid partitions.
- V3: Add self-check (missing boundaries, invalid cases, contradictions).
- V4: Add input_type + technique selection (EP/BVA, decision table, state transition, combinatorial) with stricter JSON-only output and stronger self-check.
- Specialized multi-step prompts:
  - EP/BVA uses two-step generation: (1) ECP+BVA analysis, (2) test case generation from analysis.
  - Decision Table uses three-step generation: (1) conditions/actions, (2) rules, (3) test cases.

## 8. Example Prompt (V1)

You are a software testing assistant.
Given the following requirements, do:
1) list input variables
2) derive equivalence partitions (valid/invalid)
3) derive boundary values
4) produce concrete test cases with expected results
Return in JSON format.

Requirement: {requirement_text}

## 9. Evaluation Plan

- Coverage: percentage of identified variables covered by test cases.
- Accuracy: manual review of invalid or inconsistent cases.
- Generalizability: test on 2-3 different scenarios.

Suggested measurable checklist (for report):
- Variable coverage: \(|\{v \in input\_variables : v \text{ appears in any test case inputs}\}| / |input\_variables|\)
- Negative-case coverage: at least 1 invalid test per major constraint
- Technique fidelity:
  - EP/BVA: partitions include valid+invalid; boundary sets include below/at/above
  - Decision table: rule columns covered by tests (summarized in notes)
  - State transition: transitions + invalid transitions covered (summarized in notes)
  - Combinatorial: pairwise-focused across selected variables (value sets summarized in notes)

## 10. Team Handoff Notes

- Teammates choose the scenario and provide detailed requirements.
- Teammates run prompt iterations and refine outputs.
- This document defines the framework and API contract only.

---

# 设计文档 - 基于 LLM 的黑盒测试工具

## 1. 目标与范围

本工具提供一个轻量黑盒测试框架：输入需求文本，抽取输入变量与约束，使用等价类划分（EP）与边界值分析（BVA）生成测试用例。重点在工具架构、API 接入与 prompt 迭代，不要求完整闭环执行。

## 2. 关键决策

- 界面：最小化单页表单，输入需求并展示 JSON。
- 架构：单体服务，不强制前后端分离。
- 技术栈：FastAPI + Jinja2 + OpenAI API。
- 输出：结构化 JSON，便于后续处理。

## 3. 系统架构

- Web UI（Jinja2）：需求输入表单。
- API（FastAPI）：调用 LLM 并返回 JSON。
- Prompt 管理：版本化模板（V1/V2/V3）。
- 日志：记录模型、温度、prompt 版本、时间等元数据。

## 4. 功能需求

- FR-1：接收需求文本。
- FR-2：输出结构化 JSON。
- FR-3：至少支持 EP 与 BVA。
- FR-4：支持 prompt 版本化与迭代说明。
- FR-5：提供最小化 UI 以验证接口。

## 5. 非功能需求

- NFR-1：小到中等需求应快速响应。
- NFR-2：尽量可重复（低温度）。
- NFR-3：API 失败需有清晰错误提示与重试。

## 6. API 设计

### POST /api/generate

请求 JSON：
{
  "requirements": "...",
  "prompt_version": "v1",
  "model": "gpt-4o-mini",
  "temperature": 0.2
}

响应 JSON：
{
  "input_variables": ["..."],
  "equivalence_partitions": [
    {
      "id": "EP1",
      "description": "...",
      "valid": true
    }
  ],
  "boundary_values": [
    {
      "variable": "...",
      "values": ["...", "...", "..."]
    }
  ],
  "test_cases": [
    {
      "id": "TC1",
      "scenario": "...",
      "inputs": {
        "var1": "..."
      },
      "expected": "..."
    }
  ],
  "notes": "..."
}

## 7. Prompt 策略

- V1：变量 + EP + BVA + 用例。
- V2：固定 JSON 结构与 valid/invalid。
- V3：自检缺失边界、无效用例、矛盾点。

## 8. 示例 Prompt（V1）

You are a software testing assistant.
Given the following requirements, do:
1) list input variables
2) derive equivalence partitions (valid/invalid)
3) derive boundary values
4) produce concrete test cases with expected results
Return in JSON format.

Requirement: {requirement_text}

## 9. 评价计划

- 覆盖率：用例覆盖变量比例。
- 准确性：人工检查无效/不一致用例。
- 泛化性：至少 2-3 个不同场景。

## 10. 交接说明

- 组员选择情景并提供详细需求。
- 组员执行 prompt 迭代并完善结果。
- 本文档仅定义框架与 API 约定。
