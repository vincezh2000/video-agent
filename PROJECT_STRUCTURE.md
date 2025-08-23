# Showrunner Agents 项目结构分析

## 🎯 项目概述
基于 Fable Studio 的 SHOW-1 研究，实现自动生成完整电视剧集（22分钟）的多智能体系统。

## 🏗️ 系统架构

### 核心工作流程
```
1. 多智能体模拟 (可选) → 2. LLM链式生成 → 3. 戏剧增强 → 4. 多模态输出
```

## 📁 项目文件结构

### 1. **入口文件**
- `src/main.py` - 完整系统的主入口（包含模拟）
- `example_skip_simulation.py` - 跳过模拟的快速生成入口
- `example_generate_episode.py` - 简化的剧集生成示例

### 2. **核心模块** (`src/`)

#### 🤖 **agents/** - 智能体系统
- `character_agent.py` - 角色智能体实现
  - 个性模型（五大人格特质）
  - 记忆系统
  - 决策引擎
  - 反思机制（Reverie）

#### 🎭 **drama/** - 戏剧增强
- `drama_operators.py` - 戏剧操作符
  - 反转（Reversal）
  - 伏笔（Foreshadowing）
  - 悬念（Cliffhanger）
  - 升级（Escalation）
  - 回调（Callback）

#### 🧠 **llm/** - LLM处理
- `llm_client.py` - LLM客户端（支持GPT-4.1）
- `prompt_chain.py` - 提示链系统
  - 概念生成 → 判别 → 结构化 → 对话 → 润色
- `prompts.py` - 提示模板库

#### 🌍 **simulation/** - 模拟引擎
- `simulation_engine.py` - 世界模拟核心
- `run_simulation.py` - 模拟运行器
  - 时间步进系统
  - 事件生成
  - 交互管理

#### 🎬 **generation/** - 场景生成
- `scene_compiler.py` - 场景编译器
  - 场景组装
  - 对话生成
  - 动作描述

#### 🔊 **rendering/** - 输出渲染
- `audio_renderer.py` - 音频渲染（预留接口）

#### 📊 **models/** - 数据模型
- `episode_models.py` - 剧集数据结构
  - Episode
  - Scene
  - Character
  - Dialogue

### 3. **配置文件**
- `config/default_config.yaml` - 默认系统配置
- `config_direct_mode.yaml` - 直接生成模式配置
- `.env` - 环境变量（API密钥等）

### 4. **文档**
- `CLAUDE.md` - Claude AI的项目指导
- `SHOWRUNNER_SYSTEM_ARCHITECTURE.md` - 系统架构详解
- `SHOWRUNNER_DETAILED_DESIGN.md` - 详细设计文档
- `GENERATION_PROCESS_SUMMARY.md` - 生成流程总结

## 🔄 数据流

### 完整流程（带模拟）
```mermaid
graph LR
    A[用户输入] --> B[角色创建]
    B --> C[多智能体模拟]
    C --> D[模拟数据]
    D --> E[LLM提示链]
    E --> F[场景生成]
    F --> G[戏剧增强]
    G --> H[输出文件]
```

### 快速流程（跳过模拟）
```mermaid
graph LR
    A[用户输入] --> B[预定义角色]
    B --> C[LLM提示链]
    C --> D[场景生成]
    D --> E[戏剧增强]
    E --> F[输出文件]
```

## 🎯 关键特性

### 1. **多智能体模拟**
- 自主角色行为
- 基于性格的决策
- 记忆和学习系统
- 社交网络动态

### 2. **提示链系统**
- 多步LLM处理
- 每步作为前一步的判别器
- 自动质量控制
- 失败重试机制

### 3. **戏剧模式**
- ABABC情节交织
- 三幕结构
- 自动张力曲线
- 高潮点检测

### 4. **输出格式**
- JSON结构化数据
- 剧本格式文本
- 时间戳版本控制
- 元数据追踪

## 🚀 使用方式

### 1. 完整系统运行
```bash
python src/main.py --title "Episode Title" --synopsis "Synopsis" --simulation-hours 3
```

### 2. 快速生成（跳过模拟）
```bash
python example_skip_simulation.py
```

### 3. 自定义配置
```bash
python src/main.py --config custom_config.yaml --characters-file characters.json
```

## 📊 输出结构

```json
{
  "title": "剧集标题",
  "theme": "主题",
  "concept": {
    "central_conflict": "核心冲突",
    "stakes": "利害关系",
    "urgency_driver": "紧迫性驱动"
  },
  "scenes": [
    {
      "scene_number": 1,
      "location": "地点",
      "dialogue": [...],
      "dramatic_elements": [...]
    }
  ],
  "metadata": {
    "generated_at": "时间戳",
    "model_used": "gpt-4.1"
  }
}
```

## 🔧 技术栈
- Python 3.10+
- OpenAI GPT-4.1 API
- asyncio（异步处理）
- pydantic（数据验证）
- loguru（日志系统）

## 💡 创新点
1. **解决空白页问题** - 通过模拟提供上下文
2. **解决随机性问题** - 多智能体产生创意
3. **延迟隐藏** - 异步生成和缓冲系统
4. **质量保证** - 多重验证和阈值控制

## 🎬 生成质量指标
- 角色一致性: 0.8+
- 叙事连贯性: 0.85+
- 对话自然度: 0.75+
- 戏剧张力: 动态评估