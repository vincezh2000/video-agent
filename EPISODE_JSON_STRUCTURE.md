# Episode JSON Output Structure Documentation

## 概述

生成的剧集JSON文件包含完整的电视剧集结构，从高层概要到详细的场景对话。这个格式设计用于支持多种输出形式，包括剧本、音频生成和可能的视频渲染。

## JSON结构层次

```
Episode (剧集)
├── Metadata (元数据)
├── Outline (大纲)
│   └── Acts (幕)
│       └── Scenes Summary (场景摘要)
└── Scenes (详细场景)
    ├── Description (描述)
    ├── Dialogue (对话)
    └── Dramatic Elements (戏剧元素)
```

## 顶层字段

### 1. 基本信息
```json
{
  "title": "The Algorithm's Edge",        // 剧集标题
  "synopsis": "...",                      // 剧集简介
  "themes": ["ethics vs ambition", ...],  // 主题列表
  "genre": "techno-thriller",             // 类型
  "tone": "tense"                         // 基调
}
```

### 2. Outline (大纲结构)
```json
"outline": {
  "title": "剧集标题",
  "logline": "一句话剧情概括",
  "acts": [...]  // 幕的数组
  "total_duration_seconds": 1320  // 总时长（秒）
}
```

#### Acts (幕) 结构
```json
{
  "act_number": 1,           // 幕号（通常1-4）
  "scenes": [                // 该幕中的场景列表
    {
      "scene_number": 1,     // 场景号
      "plot_line": "A",      // 情节线（A/B/C等）
      "location": "The Lab", // 地点
      "characters": ["Alex Chen"],  // 出场角色
      "summary": "场景概要",
      "duration_seconds": 90 // 场景时长
    }
  ]
}
```

### 3. Scenes (详细场景)

每个场景包含完整的表演信息：

```json
{
  "scene_number": 1,              // 场景编号
  "act_number": 1,                // 所属幕
  "location": "The Lab",          // 地点
  "time": "",                     // 时间（白天/夜晚等）
  "characters": ["Alex Chen"],    // 出场角色列表
  "description": "详细的场景描述，包括环境、氛围、动作等",
  "dialogue": [...],              // 对话数组
  "dramatic_operators": [...],    // 戏剧手法
  "turning_points": [],           // 转折点
  "emotional_arc": "",            // 情感曲线
  "quality_score": 0.96,          // 质量评分
  "coherence_status": "pass",     // 连贯性状态
  "metadata": {...}               // 元数据
}
```

#### Dialogue (对话) 结构

每条对话包含丰富的表演信息：

```json
{
  "character": "Alex Chen",        // 说话角色
  "line": "对话内容",               // 台词
  "subtext": "潜台词",             // 角色真实想法/意图
  "emotion": "anxious",           // 情绪状态
  "action": "动作描述"             // 伴随动作
}
```

**情绪类型**：
- `anxious` - 焦虑
- `impatient` - 不耐烦
- `urgent` - 紧急
- `frustrated` - 沮丧
- `alarmed` - 惊恐
- `tense` - 紧张
- `horrified` - 恐惧
- `desperate` - 绝望
- `angry` - 愤怒
- `panicked` - 恐慌
- `pleading` - 恳求

#### Dramatic Operators (戏剧手法)

```json
{
  "type": "foreshadowing",       // 类型（预示）
  "name": "Symbolic Object",     // 具体手法名称
  "intensity": 0.3               // 强度（0-1）
}
```

**戏剧手法类型**：
- `foreshadowing` - 预示/伏笔
- `reversal` - 反转
- `callback` - 回调/呼应
- `escalation` - 升级/递进
- `irony` - 讽刺
- `parallel` - 平行
- `cliffhanger` - 悬念
- `revelation` - 揭示
- `conflict` - 冲突
- `complication` - 复杂化

## Plot Lines (情节线)

剧集使用多条情节线交织叙事：
- **A线**：主线剧情
- **B线**：副线剧情
- **C线**：第三条线（通常是个人/家庭线）

情节线模式（如 `ABABCAB`）决定场景如何交替展现不同故事线。

## 质量控制字段

### Quality Score (质量评分)
- 范围：0.0 - 1.0
- 含义：场景生成质量的综合评分
- 阈值：通常 > 0.6 为可接受

### Coherence Status (连贯性状态)
- `pass` - 通过连贯性检查
- `fail` - 未通过，需要修正

## 特殊角色

- **AI System** - 系统/机器角色
- **off-screen** - 画外音/未出场角色
- **Family** - 家庭成员（群体角色）

## 使用场景

这个JSON结构支持多种用途：

1. **剧本生成**：转换为标准剧本格式
2. **音频制作**：为每个角色生成语音
3. **故事板**：可视化场景布局
4. **制作管理**：计算时长、场景调度
5. **质量分析**：评估剧情连贯性和戏剧张力

## 数据流向

```
JSON Episode
    ├→ Screenplay Formatter → 剧本文档
    ├→ Audio Renderer → 音频文件
    ├→ Timeline Generator → 时间轴
    └→ Analytics Engine → 质量报告
```

## 扩展字段（可选）

生成的JSON可能包含额外字段：

```json
{
  "audio_manifest": {...},        // 音频生成信息
  "visual_references": [...],     // 视觉参考
  "production_notes": {...},      // 制作笔记
  "simulation_data": {...},       // 模拟数据
  "metadata": {
    "generated_at": "时间戳",
    "generation_time_seconds": 120,
    "system_version": "1.0.0",
    "config": {...}
  }
}
```

## 示例解读

以 `latest_episode_mock.json` 为例：

1. **标题**："The Algorithm's Edge" - 科技惊悚剧
2. **主题**：道德vs野心、导师与学生、创新的代价
3. **结构**：4幕14场，总时长22分钟
4. **情节线**：
   - A线：Alex的AI突破和道德困境
   - B线：团队内部冲突
   - C线：家庭影响
5. **戏剧张力**：通过预示、警告等手法构建紧张氛围
6. **角色动态**：
   - Alex Chen：主角，面临道德选择
   - Sam：导师/合作者，有自己的议程
   - Jordan Park：竞争对手
   - AI System：威胁性的系统角色

这个结构确保了从概念到最终制作的完整工作流支持。