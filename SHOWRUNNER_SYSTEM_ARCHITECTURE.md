# Showrunner System Architecture Design
基于流程图的详细系统架构设计

## 1. 系统总体架构

### 1.1 核心数据流
```
User Input → Simulation → LLM Processing → Scene Generation → Multi-modal Output
```

### 1.2 主要组件
1. **输入层**: User + Agents
2. **数据层**: Simulation Data
3. **处理层**: Large Language Model + Prompt-Chain
4. **生成层**: Scene Generation (Casting + DrOps + Plot Pattern)
5. **渲染层**: Staging System + Camera System + Voice Generation
6. **输出层**: Playback

## 2. 详细模块设计

### 2.1 用户输入模块 (User Input Module)
```python
class UserInputModule:
    """处理用户输入和初始故事概念"""
    
    def __init__(self):
        self.input_types = ['title', 'synopsis', 'major_events', 'themes']
        self.validation_rules = {}
        
    def process_input(self, raw_input: Dict) -> StoryContext:
        """处理和验证用户输入"""
        - 解析用户意图
        - 提取关键故事元素
        - 创建初始上下文
        
    def enhance_with_suggestions(self, context: StoryContext) -> StoryContext:
        """基于输入提供创意建议"""
        - 分析输入完整性
        - 提供缺失元素建议
        - 返回增强的上下文
```

### 2.2 智能体系统 (Agent System)
```python
class AgentSystem:
    """管理多智能体交互和行为"""
    
    def __init__(self):
        self.agents = []  # 活跃智能体列表
        self.agent_factory = AgentFactory()
        
    def spawn_agents(self, story_context: StoryContext) -> List[Agent]:
        """根据故事需求生成智能体"""
        - 分析所需角色
        - 创建智能体实例
        - 设置初始状态和关系
        
    def execute_actions(self, time_step: int) -> List[Action]:
        """执行智能体动作"""
        - 收集所有智能体决策
        - 解决冲突
        - 返回动作列表
```

### 2.3 模拟数据收集器 (Simulation Data Collector)
```python
class SimulationDataCollector:
    """收集和组织模拟数据作为创意燃料"""
    
    def __init__(self):
        self.event_buffer = EventBuffer()
        self.state_tracker = StateTracker()
        
    def collect_simulation_data(self, actions: List[Action]) -> SimulationData:
        """收集模拟运行数据"""
        - 记录智能体动作
        - 追踪状态变化
        - 提取有趣事件
        - 识别冲突和张力点
        
    def prepare_prompt_context(self, data: SimulationData) -> PromptContext:
        """准备LLM提示上下文"""
        - 过滤相关数据
        - 组织时间线
        - 突出关键冲突
        - 包含角色动机
```

### 2.4 LLM处理核心 (LLM Processing Core)
```python
class LLMProcessor:
    """大语言模型处理核心"""
    
    def __init__(self, model_config: ModelConfig):
        self.generator = LLMGenerator(model_config)
        self.evaluator = LLMEvaluator(model_config)
        self.prompt_chain = PromptChain()
        
    def generate_content(self, context: PromptContext) -> GeneratedContent:
        """生成内容的主流程"""
        - 构建初始提示
        - 执行生成
        - 收集结果
        
    def evaluate_quality(self, content: GeneratedContent) -> QualityScore:
        """评估生成内容质量"""
        - 检查一致性
        - 评估创意性
        - 验证角色真实性
        
    def iterate_improvement(self, content: GeneratedContent, score: QualityScore):
        """基于评估迭代改进"""
        - 识别弱点
        - 生成改进建议
        - 重新生成问题部分
```

### 2.5 提示链管理器 (Prompt-Chain Manager)
```python
class PromptChainManager:
    """管理多步提示链流程"""
    
    def __init__(self):
        self.chain_stages = [
            'concept_generation',
            'scene_breakdown', 
            'character_casting',
            'dialogue_generation',
            'dramatic_enhancement'
        ]
        
    async def execute_chain(self, initial_context: Dict) -> ChainResult:
        """执行完整提示链"""
        results = {}
        context = initial_context
        
        for stage in self.chain_stages:
            stage_result = await self.execute_stage(stage, context)
            results[stage] = stage_result
            context = self.update_context(context, stage_result)
            
        return self.compile_results(results)
        
    def execute_stage(self, stage: str, context: Dict) -> StageResult:
        """执行单个链阶段"""
        - 选择合适的提示模板
        - 注入上下文数据
        - 调用LLM
        - 后处理结果
```

### 2.6 场景生成器 (Scene Generator)
```python
class SceneGenerator:
    """生成具体场景内容"""
    
    def __init__(self):
        self.casting_director = CastingDirector()
        self.drama_operator = DramaOperator()
        self.plot_pattern_manager = PlotPatternManager()
        
    def generate_scene(self, chain_result: ChainResult) -> Scene:
        """生成单个场景"""
        # 1. 角色选择
        cast = self.casting_director.select_cast(chain_result.characters)
        
        # 2. 应用戏剧操作符
        enhanced_content = self.drama_operator.apply_operators(
            chain_result.raw_content,
            ['reversal', 'foreshadowing', 'callback']
        )
        
        # 3. 确定剧情模式
        plot_structure = self.plot_pattern_manager.determine_pattern(
            enhanced_content,
            'ABABCAB'  # 示例模式
        )
        
        return Scene(cast, enhanced_content, plot_structure)
```

### 2.7 角色导演 (Casting Director)
```python
class CastingDirector:
    """管理场景角色分配"""
    
    def select_cast(self, available_characters: List[Character]) -> Cast:
        """为场景选择角色"""
        - 分析场景需求
        - 考虑角色可用性
        - 平衡屏幕时间
        - 确保叙事连贯性
        
    def assign_roles(self, cast: Cast, scene_type: str) -> RoleAssignment:
        """分配场景中的角色功能"""
        - 主角/配角分配
        - 冲突角色设定
        - 情感支撑角色
```

### 2.8 戏剧操作符系统 (Drama Operators System)
```python
class DramaOperatorSystem:
    """应用戏剧技巧增强场景"""
    
    operators = {
        'reversal': ReversalOperator(),
        'foreshadowing': ForeshadowingOperator(),
        'callback': CallbackOperator(),
        'escalation': EscalationOperator(),
        'cliffhanger': CliffhangerOperator()
    }
    
    def apply_operators(self, content: Content, operator_list: List[str]) -> Content:
        """应用选定的戏剧操作符"""
        enhanced_content = content
        
        for op_name in operator_list:
            operator = self.operators[op_name]
            if operator.is_applicable(enhanced_content):
                enhanced_content = operator.apply(enhanced_content)
                
        return enhanced_content
        
    def auto_select_operators(self, scene_context: Dict) -> List[str]:
        """基于场景上下文自动选择操作符"""
        - 分析场景位置（开始/中间/结尾）
        - 考虑情感曲线
        - 检查前置场景
        - 返回推荐操作符
```

### 2.9 剧情模式管理器 (Plot Pattern Manager)
```python
class PlotPatternManager:
    """管理剧情线交织模式"""
    
    def __init__(self):
        self.patterns = {
            'linear': 'AAAA',
            'alternating': 'ABAB',
            'complex': 'ABABCAB',
            'climactic': 'AABBBCC'
        }
        
    def determine_pattern(self, episode_length: int, storylines: List[Storyline]) -> str:
        """确定剧集的剧情模式"""
        - 分析故事线数量
        - 考虑剧集长度
        - 优化观众参与度
        - 返回最佳模式
        
    def schedule_scenes(self, scenes: List[Scene], pattern: str) -> List[Scene]:
        """按模式安排场景顺序"""
        - 将场景分配到故事线
        - 按模式重新排序
        - 确保过渡流畅
```

### 2.10 舞台系统 (Staging System)
```python
class StagingSystem:
    """处理场景的视觉呈现"""
    
    def __init__(self):
        self.location_manager = LocationManager()
        self.prop_manager = PropManager()
        self.lighting_director = LightingDirector()
        
    def setup_scene(self, scene: Scene) -> StagedScene:
        """设置场景舞台"""
        # 1. 确定位置
        location = self.location_manager.get_location(scene.location_id)
        
        # 2. 放置道具
        props = self.prop_manager.arrange_props(location, scene.requirements)
        
        # 3. 设置光照
        lighting = self.lighting_director.design_lighting(scene.mood)
        
        return StagedScene(location, props, lighting)
        
    def spawn_characters(self, cast: Cast, staged_scene: StagedScene):
        """在场景中生成角色"""
        - 确定初始位置
        - 设置角色朝向
        - 应用初始动画状态
```

### 2.11 摄像系统 (Camera System)
```python
class CameraSystem:
    """智能摄像机控制系统"""
    
    def __init__(self):
        self.shot_composer = ShotComposer()
        self.camera_controller = CameraController()
        
    def plan_shots(self, scene: Scene) -> ShotList:
        """规划场景镜头"""
        - 分析对话节奏
        - 确定关键时刻
        - 设计镜头序列
        
    def execute_camera_work(self, shot_list: ShotList, real_time: bool = False):
        """执行摄像机运动"""
        - 平滑过渡
        - 跟踪说话者
        - 捕捉反应镜头
        - 维持视觉连贯性
```

### 2.12 语音生成系统 (Voice Generation System)
```python
class VoiceGenerationSystem:
    """处理对话语音合成"""
    
    def __init__(self):
        self.voice_bank = VoiceBank()  # 预克隆的角色声音
        self.tts_engine = TTSEngine()
        self.audio_buffer = AudioBuffer()
        
    def generate_dialogue_audio(self, dialogue: Dialogue, character: Character) -> Audio:
        """生成对话音频"""
        # 1. 获取角色声音模型
        voice_model = self.voice_bank.get_voice(character.id)
        
        # 2. 分析情感和语调
        prosody = self.analyze_prosody(dialogue.text, dialogue.emotion)
        
        # 3. 生成音频
        audio = self.tts_engine.synthesize(
            text=dialogue.text,
            voice=voice_model,
            prosody=prosody
        )
        
        return audio
        
    def buffer_management(self, dialogue_queue: Queue[Dialogue]):
        """管理音频缓冲以避免延迟"""
        - 预生成下一个音频
        - 维持缓冲区
        - 处理实时请求
```

### 2.13 播放控制器 (Playback Controller)
```python
class PlaybackController:
    """控制最终内容播放"""
    
    def __init__(self):
        self.video_renderer = VideoRenderer()
        self.audio_mixer = AudioMixer()
        self.subtitle_generator = SubtitleGenerator()
        
    def playback_episode(self, episode: Episode):
        """播放完整剧集"""
        for scene in episode.scenes:
            self.play_scene(scene)
            
    def play_scene(self, scene: Scene):
        """播放单个场景"""
        # 1. 渲染视频流
        video_stream = self.video_renderer.render(scene.visuals)
        
        # 2. 混合音频轨道
        audio_stream = self.audio_mixer.mix([
            scene.dialogue_audio,
            scene.ambient_audio,
            scene.music_track
        ])
        
        # 3. 生成字幕
        subtitles = self.subtitle_generator.generate(scene.dialogue)
        
        # 4. 同步播放
        self.synchronized_playback(video_stream, audio_stream, subtitles)
```

## 3. 数据结构定义

### 3.1 核心数据类型
```python
@dataclass
class StoryContext:
    title: str
    synopsis: str
    themes: List[str]
    major_events: List[str]
    simulation_data: Optional[SimulationData] = None

@dataclass
class Scene:
    id: str
    location: Location
    cast: List[Character]
    dialogue: List[Dialogue]
    plot_line: str  # 'A', 'B', 'C'等
    drama_operators: List[str]
    duration: float

@dataclass
class Character:
    id: str
    name: str
    personality: PersonalityProfile
    voice_model: VoiceModel
    current_state: CharacterState
    relationships: Dict[str, Relationship]

@dataclass
class Dialogue:
    character_id: str
    text: str
    emotion: str
    subtext: Optional[str]
    timing: DialogueTiming

@dataclass
class SimulationData:
    events: List[Event]
    agent_states: Dict[str, AgentState]
    environment_state: EnvironmentState
    timestamp: int
```

## 4. 系统集成流程

### 4.1 主执行流程
```python
class ShowrunnerSystem:
    """主系统协调器"""
    
    def __init__(self):
        self.modules = {
            'input': UserInputModule(),
            'agents': AgentSystem(),
            'simulation': SimulationDataCollector(),
            'llm': LLMProcessor(),
            'scene_gen': SceneGenerator(),
            'staging': StagingSystem(),
            'camera': CameraSystem(),
            'voice': VoiceGenerationSystem(),
            'playback': PlaybackController()
        }
        
    async def generate_episode(self, user_input: Dict) -> Episode:
        """生成完整剧集的主流程"""
        
        # 1. 处理用户输入
        story_context = self.modules['input'].process_input(user_input)
        
        # 2. 初始化智能体
        agents = self.modules['agents'].spawn_agents(story_context)
        
        # 3. 运行模拟收集数据
        simulation_data = await self.run_simulation(agents, story_context)
        
        # 4. 通过LLM处理生成场景
        scenes = await self.generate_scenes(simulation_data, story_context)
        
        # 5. 渲染和准备播放
        episode = await self.prepare_episode(scenes)
        
        return episode
        
    async def run_simulation(self, agents: List[Agent], context: StoryContext) -> SimulationData:
        """运行模拟循环"""
        simulation_time = 0
        max_time = context.simulation_duration
        
        while simulation_time < max_time:
            # 执行智能体动作
            actions = self.modules['agents'].execute_actions(simulation_time)
            
            # 收集数据
            self.modules['simulation'].collect_simulation_data(actions)
            
            simulation_time += 1
            
        return self.modules['simulation'].get_collected_data()
```

## 5. 关键设计决策

### 5.1 并发处理
- **场景生成**: 并行处理多个场景的LLM请求
- **语音合成**: 提前缓冲避免播放延迟
- **渲染**: 视频和音频轨道并行处理

### 5.2 质量控制
- **多步评估**: Generation → Evaluation → Iteration
- **一致性检查**: 角色行为、世界规则、剧情连贯性
- **自动回退**: 生成失败时的模板备选方案

### 5.3 性能优化
- **模型选择**: 关键部分用GPT-4，次要部分用GPT-3.5
- **缓存策略**: 缓存常用提示和生成结果
- **增量生成**: 边生成边播放，不等待全部完成

### 5.4 扩展性设计
- **模块化架构**: 各组件独立可替换
- **插件系统**: 支持自定义戏剧操作符和剧情模式
- **API接口**: 标准化的模块间通信

## 6. 实现优先级

### Phase 1: 核心功能
1. LLM集成和提示链
2. 基础场景生成
3. 简单的角色和对话

### Phase 2: 智能体系统
1. 智能体初始化
2. 基础模拟循环
3. 数据收集

### Phase 3: 增强功能
1. 戏剧操作符
2. 剧情模式管理
3. 高级角色分配

### Phase 4: 多模态输出
1. 语音生成集成
2. 视觉渲染
3. 完整播放系统

## 7. 测试策略

### 7.1 单元测试
- 每个模块的独立功能测试
- 数据结构验证
- 边界条件处理

### 7.2 集成测试
- 模块间通信
- 数据流完整性
- 端到端场景生成

### 7.3 质量测试
- 生成内容的一致性
- 角色行为的真实性
- 剧情的连贯性

### 7.4 性能测试
- 生成延迟测量
- 并发处理能力
- 资源使用监控