# Design Document - LLM-Based Black-Box Testing Tool

## 1. Goal and Scope

This tool provides a lightweight framework for black-box testing using an LLM. It accepts requirement text, extracts input variables and constraints, and generates test cases via equivalence partitioning (EP) and boundary value analysis (BVA). The focus is on tool architecture, API integration, and prompt iteration, not full end-to-end test execution.

## 2. Key Decisions

- UI: Minimal, single-page web form for input and JSON output display.
- Architecture: Monolith (no strict front-end/back-end separation).
- Stack: FastAPI + Jinja2 + OpenAI API.
- Output: Structured JSON for downstream processing.

## 3. System Architecture

- Web UI (Jinja2): Simple form for requirement input.
- API (FastAPI): Endpoint that calls the LLM and returns JSON.
- Prompt Manager: Versioned prompt templates (V1/V2/V3).
- Logging: Store request metadata (model, temperature, prompt version, time).

## 4. Functional Requirements

- FR-1: Accept requirement text as input.
- FR-2: Generate structured JSON output.
- FR-3: Support EP and BVA (at minimum).
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
  "notes": "..."
}

## 7. Prompt Strategy

- V1: Extract variables + EP + BVA + test cases.
- V2: Force JSON schema and explicit valid/invalid partitions.
- V3: Add self-check (missing boundaries, invalid cases, contradictions).

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
