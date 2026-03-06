---
name: c-end-requirement-analysis
description: 面向C端产品的需求挖掘与需求分析技能，覆盖场景分析、用户任务分析、功能分析、信息架构分析、需求优先级评估与范围界定。用于需求澄清、方案评估、版本规划、需求评审材料准备、从访谈/反馈/数据中提炼需求、输出结构化需求分析文档与Word交付件等任务。
---

# C-End Requirement Analysis

## Overview

将零散信息（业务目标、用户反馈、行为数据、竞品输入）转化为“可评审、可排期、可交付”的需求分析结果。
优先输出结论和决策依据，避免空泛叙述。

## Workflow

1. 定义分析边界
- 明确业务目标、目标用户、场景范围、版本范围、时间范围。
- 统一术语和口径（用户、活跃、转化、成功动作等）。
- 若输入不完整，先列出缺口与假设，再继续分析。

2. 场景分析
- 用户分层：新用户/活跃用户/沉默用户/高价值用户。
- 场景拆解：触发条件、用户动机、环境约束、任务路径、失败点。
- 输出“场景优先级”：高频、高痛、高价值优先。
- 需要详细方法时读取 [references/scenario-and-requirement-framework.md](references/scenario-and-requirement-framework.md)。

3. 需求分析
- 将场景问题转化为需求项：目标、用户价值、业务价值、验收标准。
- 功能分析：主功能、支撑功能、边界功能、非目标功能。
- 信息架构分析：对象模型、关键字段、页面层级、导航关系、状态流转。
- 非功能需求：性能、稳定性、风控、合规、可观测性。

4. 优先级与范围管理
- 使用 RICE 或 MoSCoW 输出优先级。
- 区分 MVP、V1、V2；明确“先不做”清单。
- 标注依赖与风险：技术依赖、流程依赖、资源依赖、时间风险。

5. 形成交付件
- 先生成结构化文本摘要（结论优先，页内可快速浏览）。
- 再生成 Word 文档：使用 `scripts/generate_requirement_docx.py`。
- Word 内容结构参考 [references/requirement-doc-template.md](references/requirement-doc-template.md)。

## Output Requirements

- 先给“3-5条关键结论”，再给支撑分析。
- 每个需求项必须包含：问题定义、目标、功能点、信息架构影响、验收标准、优先级。
- 表达要求：短句、可执行、可追踪；避免叙事化废话。
- 对不确定结论标注假设和置信度。

## Docx Generation

1. 按如下结构准备 JSON：

```json
{
  "title": "需求分析文档-XX项目",
  "version": "v1.0",
  "date": "2026-03-03",
  "author": "产品经理",
  "summary": ["结论1", "结论2"],
  "sections": [
    {
      "heading": "1. 场景分析",
      "paragraphs": ["核心背景", "关键洞察"],
      "bullets": ["要点A", "要点B"],
      "table": {
        "headers": ["场景", "痛点", "影响", "优先级"],
        "rows": [["场景A", "痛点A", "高", "P0"]]
      }
    }
  ]
}
```

2. 运行脚本：

```bash
python3 skills/c-end-requirement-analysis/scripts/generate_requirement_docx.py \
  --input /path/to/analysis.json \
  --output /path/to/需求分析文档.docx
```

3. 交付前检查
- 标题、版本、日期、作者是否完整。
- 每章是否有结论与证据，不留空章节。
- 优先级与范围是否一致（避免 P0 进入非MVP）。

## Example Triggers

- “帮我把这个用户反馈列表做成需求分析，重点做场景分析和功能拆解。”
- “我要评审一个 C 端新功能，给我一份高级产品经理视角的需求分析文档。”
- “基于现有方案补全信息架构分析，并导出 Word 版本给研发评审。”
