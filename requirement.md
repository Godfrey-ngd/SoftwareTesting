# Assignment 1

## Requirements

The assignment requires students to design and implement (or enhance) a testing technique using AI methods (e.g., LLMs). Students may choose static testing, black-box dynamic testing, or white-box dynamic testing.

Note: This page shows the list of tools for static code analysis (external link). Black-box testing techniques include Equivalence Partitioning (EP), Boundary Value Analysis (BVA), Testing Combinations of Inputs, State Transition Testing Model Generator, Decision Table Testing. White-box testing can measure statement coverage, branch coverage, condition coverage, path coverage, d-u coverage, etc.

The tool must accept one of two input forms: (1) system requirements, or (2) a testing codebase. It should analyze the requirements or the testing codebase (or a module) to create test cases.

## Submission Artifacts

- Input: requirements or project codebase
- Tool artifacts: prompts used, model used, model-generated code
- Generated output: reported alarms (static analysis); test cases (black-box and white-box)
- Experimental analysis (accuracy, coverage, generalizability, etc.)
- Project report
- Comparison to traditional non-AI techniques, including pros and cons
- Analytical report: limitations of AI encountered and how you improved the tool in practice
- Summary

## Assessment Criteria

- Understanding of concepts: 10%
- Coherence of design and implementation: 20%
- Coverage and effectiveness/usefulness: 40%
- In-depth analysis (generalizability demonstration, reasoning, etc.): 20%
- Presentation: 10%

## Presentation

Each group has 15 minutes to present in English, covering all aspects above, followed by Q&A. Reviewers will ask questions based on submitted documents, presentation content, and expected software testing fundamentals.

Contribution is equal by default. Any changes must be requested separately and approved with signatures of all members.

## Submission

Each group must email the following to the TA one day before the presentation:

- a) Submission Artifacts: include all content above; cover page includes team ID, full names, and student IDs
- b) Final Presentation PPT: first slide includes team ID, full names, and student IDs
- Report and PPT must be PDF; test scripts must be a compressed file

## Schedule

- Submission deadline: Week 8, Monday, before 17:00
- Presentation dates: Week 8-9, Tuesday/Thursday, 10:00-11:35

## Example Submission Ex1

Title: LLM-based Dynamic Black-box Testing for Multi-Item Smart Vending Machine

Input

System Overview: The system under test is a smart vending machine deployed in a public area (e.g., subway station). The internal software, hardware control logic, and database are not visible to the tester. Testing is performed only from externally observable behavior, based on the provided requirements.

Functional Requirements

- Item selection: three categories: Drinks ($1.50-$3.00), Snacks ($2.00-$4.50), Hot food ($5.00-$10.00)
- Accepted payment methods: coins ($0.10, $0.25, $0.50, $1.00) and banknotes ($5.00, $10.00)
- Payment constraints: total inserted >= item price; change up to $5.00 only; reject if change > $5.00
- Inventory constraints: an item may become out of stock during payment

Tool Artifact

LLM Used: GPT-4o

Prompt Used

You are a software testing assistant. Given the following system overview and requirement, identify:
1) Input variables 2) Equivalence partitions (valid and invalid) 3) Boundary values 4) Concrete test cases
Requirement: {requirement_text}

Generated Output

Equivalence Partitioning (example)

ID | Description | Outcome
EP1 | Inserted amount < item price | valid
EP2 | Inserted amount > item price | invalid
...

Boundary Value Analysis (example)

Boundary | Values
Item price | $1.4, $1.5, $1.6
Payment total | $0, $1.4, $15.1
...

Sample Test Cases (example)

Test Case | Scenario | Expected Result
TC1 | Snack $3.00, paid $8.50 | Reject (change > $5)
TC2 | Snack $3.00, paid $3.50 | Payment success, return change $0.50
...

Experimental Analysis

4.1 Coverage of EP/BVA and test cases.
4.2 Missing item analysis.
4.3 Refining prompts to improve coverage, accuracy, and generalizability.

Project Report

Comparison to traditional non-AI techniques, pros and cons
Analytical report: limitations of AI and ways to improve the tool
Summary

## Example Submission Ex2

Title: LLM-based Static Analysis

Input

System Overview

Axios is a promise-based network request library that can run in both Node.js and browsers. This library is adapted from Axios v1.3.4 to be compatible with OpenHarmony while retaining its usage patterns and features.

Features

- HTTP requests
- Promise API
- Request and response interceptors
- Transformation of request and response data
- Automatic conversion of JSON data

The source code of Axios can be obtained at https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Faxios (external link).

Tool Artifact

Example Prompt

You are a static code analyzer. Analyze the following {language} code and detect potential issues.
Identify the following:
- Syntax errors
- Security vulnerabilities
- Deprecated or incompatible API usage
- Potential runtime errors
- Code quality issues
Return the results in structured JSON format:

{
  "issues": [
    {
      "line": <line_number>,
      "type": "<issue_type>",
      "description": "<detailed description>",
      "severity": "<low/medium/high>"
    }
  ]
}

Code:
{source_code}

Generated Output (example)

Issue 1:
[{
  "line": 4,
  "type": "Resource Management",
  "description": "File opened using 'open' but not managed with a context manager. If an exception occurs, the file may remain open.",
  "severity": "medium",
  "recommendation": "Use 'with open(filename, 'r') as f:' to automatically close the file.",
  "category": "Code Quality",
  "reference": "https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files"
}]

Test Case (Proof of concept)

Experimental Analysis

4.1 False alarms analysis
Refining prompts to improve accuracy
Try more projects to improve generalizability
Bug reporting and validation by developers

Project Report

Comparison to traditional non-AI techniques, pros and cons
Analytical report: limitations of AI and ways to improve the tool
Summary

## Example Submission Ex3

Title: LLM-based White-box Testing

Input

System Overview

Axios is a promise-based network request library that can run in both Node.js and browsers. This library is adapted from Axios v1.3.4 to be compatible with OpenHarmony while retaining its usage patterns and features.

Features

- HTTP requests
- Promise API
- Request and response interceptors
- Transformation of request and response data
- Automatic conversion of JSON data

The source code of Axios can be obtained at https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Faxios (external link).

Tool Artifact

Prompt

You are an expert software tester and white-box testing assistant.
Your task is to analyze the following {language} function/module and generate a set of test cases that achieve full statement coverage.
Please do the following:
- Identify all executable statements in the code.
- For each statement, generate test input values that will execute it at least once.
- Output the test cases in a structured JSON format suitable for automated testing.

Structured JSON format

{
  "function": "<function_name>",
  "test_cases": [
    {
      "input": { "<parameter_name>": <value>, ... },
      "expected_output": "<expected output or behavior>",
      "covered_statements": [<line_numbers>],
      "notes": "<optional explanation>"
    }
  ]
}

Code to analyze:
{code_snippet}

Notes

- Include edge cases if necessary to cover all branches of conditional statements.
- If a statement is unreachable due to a logic error, mark it as "unreachable".
- Provide explanations for how each test case achieves statement coverage.

Generated Output

Tested Function

Test Cases

TestCase1: Delete Specified Files
TestCase2: Exception Handling

Experimental Analysis

4.1 False alarms analysis
Refining prompts to improve accuracy
Try more projects to improve generalizability
Bug reporting and validation by developers

Project Report

Comparison to traditional non-AI techniques, pros and cons
Analytical report: limitations of AI and ways to improve the tool
Summary

---

# 作业一

## 需求

本作业要求学生使用 AI 方法（如 LLM）设计并实现（或改进）一种测试技术。可选择静态测试、黑盒动态测试或白盒动态测试。

注意：本页面包含静态代码分析工具列表（外部链接）。黑盒测试技术包括等价类划分（EP）、边界值分析（BVA）、输入组合测试、状态迁移测试模型生成、判定表测试。白盒测试可度量语句覆盖、分支覆盖、条件覆盖、路径覆盖、d-u 覆盖等。

工具必须接受两种输入之一：（1）系统需求；（2）测试代码库。工具应分析需求或测试代码库（或模块）并生成测试用例。

## 提交物

- 输入：需求或项目代码库
- 工具产物：使用的提示词、使用的模型、模型生成的代码
- 生成输出：报警/问题报告（静态分析）；测试用例（黑盒与白盒）
- 实验分析（准确率、覆盖率、泛化性等）
- 项目报告
- 与传统非 AI 技术对比及优缺点
- 分析报告：实践中遇到的 AI 局限及改进方法
- 总结

## 评分标准

- 概念理解：10%
- 设计与实现一致性：20%
- 覆盖率与有效性/实用性：40%
- 深入分析（泛化性展示、推理等）：20%
- 展示：10%

## 展示

每组需用英文进行 15 分钟展示，覆盖上述所有内容，随后进行问答。评审将基于提交材料、展示内容及应掌握的软件测试基础提问。

默认贡献均分。如需调整，须单独申请并由所有成员签字同意。

## 提交

每组需在展示前一天通过邮件提交以下材料给助教：

- a）提交物：包含上述所有内容；封面需包含队伍编号、成员姓名与学号
- b）最终展示 PPT：首页需包含队伍编号、成员姓名与学号
- 报告与 PPT 需为 PDF；测试脚本需压缩提交

## 时间安排

- 截止时间：第 8 周周一 17:00 前
- 展示时间：第 8-9 周周二/周四 10:00-11:35

## 示例提交 Ex1

标题：基于 LLM 的多商品智能售货机黑盒动态测试

输入

系统概述：被测系统为公共区域（如地铁站）部署的智能售货机。测试者无法访问内部软件、硬件控制逻辑与数据库，仅能基于需求从外部可观察行为进行测试。

功能需求

- 商品选择：三类商品：饮料（$1.50-$3.00）、零食（$2.00-$4.50）、热食（$5.00-$10.00）
- 接受支付方式：硬币（$0.10、$0.25、$0.50、$1.00）与纸币（$5.00、$10.00）
- 支付约束：投币总额需 >= 商品价格；仅找零至多 $5.00；若找零 > $5.00 则拒绝
- 库存约束：支付过程中可能缺货

工具产物

使用模型：GPT-4o

使用提示词

你是一名软件测试助手。给定系统概述与需求，请识别：
1）输入变量 2）等价类（有效/无效）3）边界值 4）具体测试用例
需求：{requirement_text}

生成输出

等价类划分（示例）

ID | 描述 | 结果
EP1 | 投入金额 < 商品价格 | 有效
EP2 | 投入金额 > 商品价格 | 无效
...

边界值分析（示例）

边界 | 取值
商品价格 | $1.4、$1.5、$1.6
支付总额 | $0、$1.4、$15.1
...

示例测试用例（示例）

用例 | 场景 | 期望结果
TC1 | 零食 $3.00，支付 $8.50 | 拒绝（找零 > $5）
TC2 | 零食 $3.00，支付 $3.50 | 支付成功，找零 $0.50
...

实验分析

4.1 EP/BVA 与测试用例覆盖情况。
4.2 缺失项分析。
4.3 通过优化提示词提升覆盖率、准确率与泛化性。

项目报告

与传统非 AI 技术对比及优缺点
分析报告：AI 局限与改进方法
总结

## 示例提交 Ex2

标题：基于 LLM 的静态分析

输入

系统概述

Axios 是一种基于 Promise 的网络请求库，可运行于 Node.js 与浏览器。该库从 Axios v1.3.4 适配为兼容 OpenHarmony，并保持原有用法与特性。

特性

- HTTP 请求
- Promise API
- 请求与响应拦截器
- 请求与响应数据转换
- JSON 数据自动转换

Axios 源码获取地址：https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Faxios（外部链接）。

工具产物

示例提示词

你是一名静态代码分析器。分析以下 {language} 代码并检测潜在问题。
请识别：
- 语法错误
- 安全漏洞
- 过时或不兼容 API 使用
- 潜在运行时错误
- 代码质量问题
请用结构化 JSON 格式返回结果：

{
  "issues": [
    {
      "line": <line_number>,
      "type": "<issue_type>",
      "description": "<detailed description>",
      "severity": "<low/medium/high>"
    }
  ]
}

代码：
{source_code}

生成输出（示例）

Issue 1:
[{
  "line": 4,
  "type": "Resource Management",
  "description": "File opened using 'open' but not managed with a context manager. If an exception occurs, the file may remain open.",
  "severity": "medium",
  "recommendation": "Use 'with open(filename, 'r') as f:' to automatically close the file.",
  "category": "Code Quality",
  "reference": "https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files"
}]

测试用例（概念验证）

实验分析

4.1 误报分析
通过优化提示词提升准确率
尝试更多项目以提升泛化性
由开发者进行缺陷报告与验证

项目报告

与传统非 AI 技术对比及优缺点
分析报告：AI 局限与改进方法
总结

## 示例提交 Ex3

标题：基于 LLM 的白盒测试

输入

系统概述

Axios 是一种基于 Promise 的网络请求库，可运行于 Node.js 与浏览器。该库从 Axios v1.3.4 适配为兼容 OpenHarmony，并保持原有用法与特性。

特性

- HTTP 请求
- Promise API
- 请求与响应拦截器
- 请求与响应数据转换
- JSON 数据自动转换

Axios 源码获取地址：https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Faxios（外部链接）。

工具产物

提示词

你是一名软件测试专家与白盒测试助手。
任务：分析以下 {language} 函数/模块，并生成实现语句覆盖率全覆盖的测试用例。
请执行：
- 识别代码中所有可执行语句。
- 为每条语句生成至少执行一次的测试输入。
- 用结构化 JSON 格式输出测试用例，以便自动化测试使用。

结构化 JSON 格式

{
  "function": "<function_name>",
  "test_cases": [
    {
      "input": { "<parameter_name>": <value>, ... },
      "expected_output": "<expected output or behavior>",
      "covered_statements": [<line_numbers>],
      "notes": "<optional explanation>"
    }
  ]
}

待分析代码：
{code_snippet}

说明

- 如需覆盖条件分支，请包含边界用例。
- 若因逻辑错误导致语句不可达，标记为 "unreachable"。
- 说明每条用例如何实现语句覆盖。

生成输出

被测函数

测试用例

用例1：删除指定文件
用例2：异常处理

实验分析

4.1 误报分析
通过优化提示词提升准确率
尝试更多项目以提升泛化性
由开发者进行缺陷报告与验证

项目报告

与传统非 AI 技术对比及优缺点
分析报告：AI 局限与改进方法
总结
