# Showrunner Agents Python Demo 系统设计文档

## 1. 项目概述

### 1.1 项目目标
基于Fable Studio的Showrunner Agents论文，实现一个Python版本的多智能体驱动的AI剧集生成系统Demo。

### 1.2 核心功能
- 多智能体模拟系统生成角色背景和事件
- 提示链(Prompt-Chaining)技术模拟创造性思维
- 整合LLM生成对话和场景描述
- 生成简单的动画视频输出

### 1.3 技术范围
- **包含**: 智能体模拟、剧本生成、对话生成、简单动画
- **不包含**: 3D渲染、复杂视觉效果、实时交互

## 2. 系统架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户接口层                              │
│                   (Streamlit/Gradio Web UI)                  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                        编排控制层                              │
│                    (Orchestration Engine)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 工作流管理器   │  │  提示链引擎   │  │  状态管理器    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                        核心服务层                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │              多智能体模拟系统                        │       │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐          │       │
│  │  │ Agent 1 │  │ Agent 2 │  │ Agent N │          │       │
│  │  └─────────┘  └─────────┘  └─────────┘          │       │
│  │         ┌─────────────────────┐                  │       │
│  │         │   Environment       │                  │       │
│  │         │   Simulator         │                  │       │
│  │         └─────────────────────┘                  │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │              AI生成服务                            │       │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │       │
│  │  │   LLM    │  │  图像生成 │  │  语音合成 │      │       │
│  │  │  Service │  │  Service │  │  Service │      │       │
│  │  └──────────┘  └──────────┘  └──────────┘      │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                        数据持久层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   MongoDB    │  │    Redis     │  │  File System │      │
│  │  (Agent Data)│  │   (Cache)    │  │   (Assets)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈选择

```yaml
# 核心框架
Python: 3.10+
Web框架: FastAPI
异步任务: Celery + Redis

# AI/ML库
LLM: LangChain + OpenAI API / Ollama (本地)
Agent框架: Mesa (多智能体模拟)
图像生成: Stable Diffusion (diffusers库)
语音合成: TTS (Coqui-TTS)

# 数据存储
主数据库: MongoDB (存储智能体数据和剧本)
缓存: Redis (任务队列和缓存)
向量数据库: ChromaDB (存储角色记忆)

# 前端展示
Web UI: Streamlit / Gradio
动画生成: Manim / MoviePy
可视化: Plotly / Matplotlib

# 开发工具
包管理: Poetry
代码格式化: Black + isort
类型检查: mypy
测试: pytest
```

## 3. 核心模块设计

### 3.1 多智能体模拟系统

#### 3.1.1 Agent类设计

```python
class CharacterAgent:
    """角色智能体基类"""
    
    def __init__(self, agent_id: str, config: Dict):
        self.id = agent_id
        self.name = config['name']
        self.backstory = config['backstory']
        self.personality = config['personality']
        self.relationships = {}  # 与其他角色的关系
        self.memories = []  # 记忆存储
        self.current_needs = {}  # 当前需求状态
        self.location = None
        self.current_activity = None
        
    def perceive(self, environment: Environment) -> List[Observation]:
        """感知环境"""
        pass
        
    def decide(self, observations: List[Observation]) -> Action:
        """决策行动"""
        pass
        
    def act(self, action: Action) -> Result:
        """执行行动"""
        pass
        
    def reflect(self, day_events: List[Event]) -> Reverie:
        """生成遐想(Reverie)"""
        pass
        
    def update_memory(self, event: Event):
        """更新记忆"""
        pass
```

#### 3.1.2 环境模拟器

```python
class SimulationEnvironment:
    """模拟环境管理器"""
    
    def __init__(self):
        self.agents: List[CharacterAgent] = []
        self.locations: List[Location] = []
        self.time: SimTime = SimTime()
        self.event_log: List[Event] = []
        
    def add_agent(self, agent: CharacterAgent):
        """添加智能体到环境"""
        pass
        
    def simulate_timestep(self):
        """模拟一个时间步"""
        # 1. 所有智能体感知环境
        # 2. 所有智能体做出决策
        # 3. 执行行动并更新环境
        # 4. 记录事件
        pass
        
    def run_simulation(self, duration: int):
        """运行完整模拟"""
        pass
```

### 3.2 提示链系统

#### 3.2.1 提示链引擎

```python
class PromptChainEngine:
    """提示链引擎 - 模拟创造性思维"""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.chain_templates = self.load_templates()
        
    async def execute_chain(self, 
                           initial_context: Dict,
                           chain_type: str) -> Dict:
        """执行提示链"""
        
        # 步骤1: 生成初始概念
        concept = await self.generate_concept(initial_context)
        
        # 步骤2: 判别和优化
        refined = await self.discriminate_refine(concept)
        
        # 步骤3: 注入戏剧元素(DrOps)
        dramatic = await self.inject_dramatic_operators(refined)
        
        # 步骤4: 最终生成
        final = await self.final_generation(dramatic)
        
        return final
        
    async def generate_concept(self, context: Dict) -> Dict:
        """生成基础概念"""
        pass
        
    async def discriminate_refine(self, concept: Dict) -> Dict:
        """判别器角色 - 评估和优化"""
        pass
        
    async def inject_dramatic_operators(self, content: Dict) -> Dict:
        """注入戏剧操作符"""
        # 反转、伏笔、悬念等
        pass
```

#### 3.2.2 戏剧指纹系统

```python
class DramaticFingerprint:
    """戏剧指纹 - 捕获特定节目风格"""
    
    def __init__(self, show_name: str):
        self.show_name = show_name
        self.style_patterns = {}
        self.dramatic_operators = []
        
    def extract_patterns(self, sample_scripts: List[str]):
        """从样本剧本提取风格模式"""
        pass
        
    def apply_fingerprint(self, content: str) -> str:
        """应用戏剧指纹到内容"""
        pass
```

### 3.3 剧集生成流程

#### 3.3.1 剧集生成器

```python
class EpisodeGenerator:
    """剧集生成主控制器"""
    
    def __init__(self):
        self.simulation = SimulationEnvironment()
        self.prompt_engine = PromptChainEngine()
        self.scene_generator = SceneGenerator()
        self.dialogue_generator = DialogueGenerator()
        self.voice_synthesizer = VoiceSynthesizer()
        
    async def generate_episode(self, 
                              synopsis: str,
                              episode_config: Dict) -> Episode:
        """生成完整剧集"""
        
        # 阶段1: 运行模拟获取上下文
        simulation_data = await self.run_simulation(episode_config)
        
        # 阶段2: 生成剧集结构
        episode_structure = await self.generate_structure(
            synopsis, simulation_data
        )
        
        # 阶段3: 生成场景
        scenes = []
        for scene_outline in episode_structure.scenes:
            scene = await self.generate_scene(scene_outline, simulation_data)
            scenes.append(scene)
            
        # 阶段4: 后处理和渲染
        episode = await self.render_episode(scenes)
        
        return episode
        
    async def generate_scene(self, 
                           outline: SceneOutline,
                           sim_data: SimulationData) -> Scene:
        """生成单个场景"""
        
        # 1. 确定参与角色
        characters = self.select_characters(outline, sim_data)
        
        # 2. 生成对话
        dialogue = await self.dialogue_generator.generate(
            characters, outline, sim_data
        )
        
        # 3. 生成场景描述
        description = await self.scene_generator.generate_description(
            outline, characters, dialogue
        )
        
        # 4. 生成语音
        voice_clips = await self.voice_synthesizer.synthesize(dialogue)
        
        return Scene(
            characters=characters,
            dialogue=dialogue,
            description=description,
            voice_clips=voice_clips
        )
```

### 3.4 渲染和输出系统

#### 3.4.1 动画渲染器

```python
class AnimationRenderer:
    """简单动画渲染器"""
    
    def __init__(self):
        self.character_sprites = {}
        self.backgrounds = {}
        
    def render_scene(self, scene: Scene) -> VideoClip:
        """渲染场景为视频片段"""
        
        # 1. 加载背景
        background = self.load_background(scene.location)
        
        # 2. 放置角色
        character_layers = self.place_characters(scene.characters)
        
        # 3. 添加对话字幕
        subtitle_layer = self.create_subtitles(scene.dialogue)
        
        # 4. 合成音频
        audio_track = self.compose_audio(scene.voice_clips)
        
        # 5. 合成最终视频
        video_clip = self.compose_video(
            background, character_layers, subtitle_layer, audio_track
        )
        
        return video_clip
```

## 4. 数据流设计

### 4.1 核心数据结构

```python
# 智能体相关
@dataclass
class AgentMemory:
    timestamp: datetime
    event_type: str
    content: Dict
    importance: float
    
@dataclass
class Reverie:
    agent_id: str
    reflection: str
    related_memories: List[AgentMemory]
    timestamp: datetime

# 剧集相关
@dataclass
class SceneOutline:
    scene_number: int
    location: str
    time: str
    summary: str
    key_events: List[str]
    participating_agents: List[str]

@dataclass
class Dialogue:
    character: str
    text: str
    emotion: str
    timing: float

@dataclass
class Scene:
    outline: SceneOutline
    dialogues: List[Dialogue]
    visual_description: str
    duration: float

@dataclass
class Episode:
    title: str
    synopsis: str
    scenes: List[Scene]
    total_duration: float
    metadata: Dict
```

### 4.2 数据流程图

```
用户输入(剧情大纲) 
    ↓
[模拟系统运行]
    ├→ 生成角色背景
    ├→ 模拟日常事件
    └→ 生成遐想记忆
    ↓
[提示链处理]
    ├→ 概念生成
    ├→ 优化判别
    └→ 戏剧增强
    ↓
[场景生成]
    ├→ 场景结构
    ├→ 对话生成
    └→ 视觉描述
    ↓
[渲染输出]
    ├→ 图像生成
    ├→ 语音合成
    └→ 视频合成
    ↓
最终剧集文件
```

## 5. API接口设计

### 5.1 RESTful API

```python
# FastAPI路由定义

@app.post("/api/v1/episodes/generate")
async def generate_episode(request: EpisodeRequest):
    """生成新剧集"""
    pass

@app.get("/api/v1/episodes/{episode_id}")
async def get_episode(episode_id: str):
    """获取剧集信息"""
    pass

@app.post("/api/v1/agents/create")
async def create_agent(agent_config: AgentConfig):
    """创建新角色智能体"""
    pass

@app.post("/api/v1/simulation/run")
async def run_simulation(sim_config: SimulationConfig):
    """运行模拟"""
    pass

@app.ws("/api/v1/stream/generation")
async def generation_stream(websocket: WebSocket):
    """WebSocket实时生成流"""
    pass
```

### 5.2 内部服务通信

```python
# 使用Celery进行异步任务处理

@celery_app.task
def simulate_agent_day(agent_id: str, day: int):
    """模拟智能体一天的活动"""
    pass

@celery_app.task
def generate_scene_async(scene_config: Dict):
    """异步生成场景"""
    pass

@celery_app.task
def render_video_async(scene_data: Dict):
    """异步渲染视频"""
    pass
```

## 6. 实现步骤

### 6.1 第一阶段：基础框架 (Week 1-2)

1. **环境搭建**
   - 项目结构初始化
   - 依赖安装和配置
   - 基础API框架搭建

2. **多智能体系统**
   - Agent基类实现
   - 环境模拟器实现
   - 基础行为模式

### 6.2 第二阶段：AI集成 (Week 3-4)

1. **LLM集成**
   - LangChain配置
   - OpenAI/Ollama接入
   - 提示模板设计

2. **提示链系统**
   - 提示链引擎实现
   - 戏剧操作符实现
   - 创造性思维模拟

### 6.3 第三阶段：生成流程 (Week 5-6)

1. **剧集生成器**
   - 场景生成逻辑
   - 对话生成系统
   - 场景串联逻辑

2. **多模态生成**
   - 图像生成集成
   - 语音合成集成
   - 简单动画生成

### 6.4 第四阶段：集成测试 (Week 7-8)

1. **系统集成**
   - 端到端流程测试
   - 性能优化
   - Bug修复

2. **UI开发**
   - Streamlit界面
   - 实时进度显示
   - 结果展示

## 7. 关键技术实现

### 7.1 智能体记忆系统

```python
class MemoryStream:
    """智能体记忆流实现"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.memories = []
        self.vector_store = ChromaDB()  # 向量数据库
        
    def add_memory(self, event: Event):
        """添加新记忆"""
        memory = AgentMemory(
            timestamp=datetime.now(),
            event_type=event.type,
            content=event.data,
            importance=self.calculate_importance(event)
        )
        self.memories.append(memory)
        
        # 存储到向量数据库
        embedding = self.generate_embedding(memory)
        self.vector_store.add(memory, embedding)
        
    def retrieve_relevant(self, context: str, k: int = 5) -> List[AgentMemory]:
        """检索相关记忆"""
        query_embedding = self.generate_embedding(context)
        relevant = self.vector_store.similarity_search(query_embedding, k)
        return relevant
        
    def generate_reverie(self, recent_events: List[Event]) -> Reverie:
        """生成遐想"""
        # 使用LLM生成反思
        relevant_memories = self.retrieve_relevant(str(recent_events))
        reflection = self.llm.generate_reflection(recent_events, relevant_memories)
        
        return Reverie(
            agent_id=self.agent_id,
            reflection=reflection,
            related_memories=relevant_memories,
            timestamp=datetime.now()
        )
```

### 7.2 提示链模板示例

```python
PROMPT_CHAIN_TEMPLATES = {
    "scene_generation": {
        "step1_concept": """
        Given the simulation context:
        Characters: {characters}
        Location: {location}
        Time: {time}
        Recent events: {events}
        
        Generate a creative scene concept that would naturally emerge from these circumstances.
        """,
        
        "step2_refine": """
        Original concept: {concept}
        
        As a story editor, evaluate this concept for:
        1. Character consistency
        2. Narrative coherence
        3. Dramatic potential
        
        Provide a refined version that enhances these aspects.
        """,
        
        "step3_dramatic": """
        Refined concept: {refined}
        
        Apply the following dramatic operators:
        - {dramatic_operators}
        
        Enhance the scene with these dramatic elements while maintaining authenticity.
        """,
        
        "step4_final": """
        Dramatic concept: {dramatic}
        Show style guide: {style_guide}
        
        Generate the final scene with:
        1. Complete dialogue
        2. Stage directions
        3. Character emotions
        4. Visual descriptions
        
        Output in structured format.
        """
    }
}
```

### 7.3 戏剧操作符实现

```python
class DramaticOperators:
    """戏剧操作符集合"""
    
    @staticmethod
    def apply_reversal(content: str) -> str:
        """应用反转"""
        prompt = f"""
        Take this scene content: {content}
        Add a surprising reversal that changes the expected outcome.
        The reversal should feel organic and character-driven.
        """
        return llm.generate(prompt)
    
    @staticmethod
    def apply_foreshadowing(content: str, future_event: str) -> str:
        """应用伏笔"""
        prompt = f"""
        Current scene: {content}
        Future event: {future_event}
        
        Subtly incorporate foreshadowing of the future event into the current scene.
        The hint should be subtle enough to not be obvious on first viewing.
        """
        return llm.generate(prompt)
    
    @staticmethod
    def apply_cliffhanger(content: str) -> str:
        """应用悬念"""
        prompt = f"""
        Scene content: {content}
        
        End this scene with a cliffhanger that creates suspense.
        The cliffhanger should raise questions that demand answers.
        """
        return llm.generate(prompt)
```

## 8. 性能优化策略

### 8.1 并发处理
- 使用asyncio进行异步IO操作
- Celery分布式任务队列
- 批量处理LLM请求

### 8.2 缓存策略
- Redis缓存生成结果
- 向量数据库索引优化
- LRU缓存常用提示模板

### 8.3 资源管理
- GPU资源池管理
- 模型懒加载
- 内存使用监控

## 9. 测试策略

### 9.1 单元测试
```python
# 智能体行为测试
def test_agent_decision_making():
    agent = CharacterAgent("test_agent", config)
    observation = Observation(type="social", data={"other_agent": "friend"})
    action = agent.decide([observation])
    assert action.type in ["interact", "ignore", "observe"]

# 提示链测试
async def test_prompt_chain():
    engine = PromptChainEngine(mock_llm)
    result = await engine.execute_chain(test_context, "scene_generation")
    assert "dialogue" in result
    assert "description" in result
```

### 9.2 集成测试
- 端到端剧集生成测试
- 多智能体交互测试
- API接口测试

### 9.3 性能测试
- 负载测试
- 响应时间测试
- 资源使用监控

## 10. 部署方案

### 10.1 开发环境
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
      
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
      
  celery:
    build: .
    command: celery -A app.celery worker --loglevel=info
    depends_on:
      - redis
```

### 10.2 生产环境
- Kubernetes部署配置
- 自动扩缩容策略
- 监控和日志系统

## 11. 项目结构

```
showrunner-agents-demo/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI主应用
│   ├── config.py                # 配置管理
│   └── api/
│       ├── __init__.py
│       ├── routes/
│       │   ├── episodes.py
│       │   ├── agents.py
│       │   └── simulation.py
│       └── schemas/
│           ├── episode.py
│           └── agent.py
├── core/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── character_agent.py
│   │   ├── memory_stream.py
│   │   └── behaviors.py
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── environment.py
│   │   ├── events.py
│   │   └── scheduler.py
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── prompt_chain.py
│   │   ├── dramatic_ops.py
│   │   ├── scene_generator.py
│   │   └── dialogue_generator.py
│   └── rendering/
│       ├── __init__.py
│       ├── animation.py
│       ├── voice_synthesis.py
│       └── video_composer.py
├── services/
│   ├── __init__.py
│   ├── llm_service.py
│   ├── image_service.py
│   ├── voice_service.py
│   └── storage_service.py
├── utils/
│   ├── __init__.py
│   ├── prompts.py
│   └── helpers.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── data/
│   ├── templates/
│   ├── assets/
│   └── models/
├── scripts/
│   ├── setup.py
│   └── run_simulation.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── USAGE.md
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## 12. 示例代码

### 12.1 完整的剧集生成示例

```python
import asyncio
from showrunner_agents import EpisodeGenerator, SimulationConfig

async def generate_sample_episode():
    # 初始化生成器
    generator = EpisodeGenerator()
    
    # 配置角色
    characters = [
        {
            "name": "Alice",
            "backstory": "A curious scientist",
            "personality": {"curious": 0.8, "cautious": 0.3}
        },
        {
            "name": "Bob", 
            "backstory": "A skeptical journalist",
            "personality": {"skeptical": 0.7, "brave": 0.6}
        }
    ]
    
    # 配置模拟
    sim_config = SimulationConfig(
        characters=characters,
        duration_hours=24,
        location="Research Lab"
    )
    
    # 剧情大纲
    synopsis = "Two unlikely partners discover a mysterious signal from space"
    
    # 生成剧集
    episode = await generator.generate_episode(
        synopsis=synopsis,
        simulation_config=sim_config,
        episode_length_minutes=5
    )
    
    # 保存结果
    episode.save("output/episode_001.mp4")
    
    return episode

# 运行示例
if __name__ == "__main__":
    asyncio.run(generate_sample_episode())
```

## 13. 未来扩展

### 13.1 短期目标 (3个月)
- 完善多智能体交互逻辑
- 提升生成内容质量
- 优化渲染效果
- 添加更多戏剧操作符

### 13.2 中期目标 (6个月)
- 训练专属模型(SHOW-1概念)
- 实现实时交互功能
- 支持多种视觉风格
- 构建剧集知识库

### 13.3 长期愿景 (1年)
- 完整的端到端电视剧制作
- 个性化AI创作者
- 跨媒体内容生成
- 开源社区建设

## 14. 总结

本设计文档提供了一个基于Python的Showrunner Agents系统完整实现方案。通过多智能体模拟、提示链技术和多模态AI的结合，我们可以实现自动化的剧集内容生成。这个Demo系统虽然在视觉效果上会比较简单，但核心的智能体交互和创意生成机制将得到完整实现。

关键成功要素：
1. 高质量的智能体模拟提供丰富上下文
2. 提示链技术确保创意连贯性
3. 戏剧操作符保持叙事张力
4. 模块化设计便于迭代优化

通过这个Demo的实现，我们将验证论文中提出的核心概念，并为未来的生产级系统奠定基础。