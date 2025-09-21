# AI斗地主游戏产品需求文档

## 产品概述

AI斗地主游戏是一款基于Python后端的在线卡牌游戏，玩家与两个AI对手进行经典斗地主对战。通过集成大语言模型API，为玩家提供智能化、个性化的游戏体验。

**核心价值主张**：融合传统斗地主玩法与前沿AI技术，提供24/7可用的智能对手，为单人玩家创造媲美多人对战的游戏体验。

**目标用户**：喜欢斗地主但缺乏稳定对手的玩家，以及对AI游戏技术感兴趣的用户。

## 技术架构设计

### 系统架构总览

采用前后端分离的分布式架构，支持高并发和水平扩展：

```
前端客户端 → Nginx负载均衡 → FastAPI游戏服务器 → AI服务层 → 大模型API
                                    ↓
                              数据存储层（Redis + MongoDB + MySQL）
```

### 后端技术栈推荐

**核心框架**：FastAPI
- 原生异步支持，性能优异（12,000+ msg/s）
- 自动生成API文档，开发效率高
- WebSocket原生支持，适合实时游戏

**数据存储策略**：
- **Redis**：游戏状态缓存、会话管理、消息队列
- **MongoDB**：游戏记录、玩家行为日志、AI决策数据
- **MySQL**：用户信息、排行榜、关键业务数据

**核心依赖**：
```python
# requirements.txt
fastapi==0.104.1
websockets==11.0
redis==5.0.1
motor==3.3.2  # MongoDB异步驱动
aiomysql==0.2.0
aiohttp==3.8.6  # AI API调用
```

### 游戏服务器架构实现

```python
# 核心游戏服务器结构
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json

class GameServer:
    def __init__(self):
        self.app = FastAPI(title="AI斗地主游戏API", version="1.0.0")
        self.connection_manager = ConnectionManager()
        self.game_manager = GameManager()
        self.ai_service = AIService()
        
    async def start_game_loop(self):
        """游戏主循环，处理所有活跃房间"""
        while True:
            active_rooms = await self.game_manager.get_active_rooms()
            tasks = [self.process_room(room) for room in active_rooms]
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.1)  # 100ms循环间隔
            
class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.connections:
            self.connections[room_id] = set()
        self.connections[room_id].add(websocket)
        
    async def broadcast_to_room(self, room_id: str, message: dict):
        if room_id in self.connections:
            disconnected = set()
            for websocket in self.connections[room_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except WebSocketDisconnect:
                    disconnected.add(websocket)
            self.connections[room_id] -= disconnected
```

## 斗地主游戏逻辑实现

### 核心游戏规则系统

**牌型识别引擎**：
```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class CardType(Enum):
    SINGLE = "single"
    PAIR = "pair"
    TRIPLE = "triple"
    TRIPLE_WITH_SINGLE = "triple_with_single"
    STRAIGHT = "straight"
    BOMB = "bomb"
    ROCKET = "rocket"

@dataclass
class CardProduct:
    cards: List[int]
    card_type: CardType
    main_value: int  # 主牌面值
    
    def is_greater_than(self, other: 'CardProduct') -> bool:
        # 炸弹可以打任何非炸弹牌型
        if self.card_type == CardType.BOMB and other.card_type != CardType.BOMB:
            return True
        if self.card_type == CardType.ROCKET:
            return True
            
        # 同类型比较主牌面值
        if self.card_type == other.card_type and len(self.cards) == len(other.cards):
            return self.main_value > other.main_value
            
        return False

class CardAnalyzer:
    @staticmethod
    def analyze_cards(cards: List[int]) -> CardProduct:
        """分析牌型并返回结果"""
        if not cards:
            return CardProduct([], CardType.SINGLE, 0)
            
        # 统计各面值数量
        counter = {}
        for card in cards:
            counter[card] = counter.get(card, 0) + 1
            
        # 根据统计结果判断牌型
        if len(cards) == 1:
            return CardProduct(cards, CardType.SINGLE, cards[0])
        elif len(cards) == 2 and len(counter) == 1:
            return CardProduct(cards, CardType.PAIR, cards[0])
        elif len(cards) == 2 and 16 in cards and 17 in cards:  # 王炸
            return CardProduct(cards, CardType.ROCKET, 17)
        # ... 其他牌型判断逻辑
```

**游戏状态管理**：
```python
class GameState:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.phase = "waiting"  # waiting, playing, ended
        self.players = {}
        self.current_player = 0
        self.last_play = None
        self.landlord = None
        self.turn_count = 0
        
    async def make_move(self, player_id: str, cards: List[int]):
        """处理玩家出牌"""
        if not self.is_player_turn(player_id):
            raise ValueError("Not player's turn")
            
        # 验证出牌合法性
        card_product = CardAnalyzer.analyze_cards(cards)
        if not self.is_legal_move(card_product):
            raise ValueError("Illegal move")
            
        # 执行出牌
        self.execute_move(player_id, card_product)
        
        # 检查游戏结束
        if self.check_game_over():
            self.end_game()
        else:
            self.next_turn()
```

## 大模型AI集成方案

### AI服务架构设计

**多模型集成策略**：
```python
class AIService:
    def __init__(self):
        self.clients = {
            'gpt4o_mini': LLMClient('https://api.openai.com/v1', api_key_1, 'gpt-4o-mini'),
            'claude_haiku': LLMClient('https://api.anthropic.com', api_key_2, 'claude-3-haiku'),
            'deepseek_v3': LLMClient('https://api.deepseek.com', api_key_3, 'deepseek-chat')
        }
        self.cache = LRUCache(maxsize=1000)
        self.rate_limiter = AsyncLimiter(20, 1)  # 每秒20个请求
        
    async def get_ai_decision(self, game_state: dict, difficulty: str = 'medium'):
        """获取AI决策"""
        # 生成缓存键
        cache_key = self.generate_cache_key(game_state, difficulty)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
            
        # 选择合适的模型
        model_client = self.select_model(difficulty, game_state)
        
        # 构建提示词
        prompt = self.build_game_prompt(game_state, difficulty)
        
        # 异步调用AI API
        async with self.rate_limiter:
            decision = await model_client.get_completion(prompt)
            
        # 解析并验证决策
        parsed_decision = self.parse_ai_decision(decision)
        self.cache[cache_key] = parsed_decision
        
        return parsed_decision
```

**提示词工程设计**：
```python
def build_game_prompt(self, game_state: dict, difficulty: str) -> str:
    prompt = f"""你是一个专业的斗地主AI玩家，当前难度等级为{difficulty}。

## 当前游戏状态
{json.dumps(game_state, ensure_ascii=False, indent=2)}

## 决策规则
1. 优先级：获胜 > 阻止对手获胜 > 牌型效率 > 保留强牌
2. 考虑因素：手牌数量、牌型组合、对手状况、阶段策略
3. 风险评估：安全出牌 vs 积极进攻

## 响应格式
请以JSON格式返回决策：
{{
    "action": "play_cards" | "pass",
    "cards": [3, 4, 5],
    "reasoning": "详细的决策理由",
    "confidence": 0.85,
    "alternative_moves": [...]
}}

请分析局势并给出最优决策。"""
    
    return prompt

def parse_ai_decision(self, response: str) -> dict:
    """解析AI响应并验证合法性"""
    try:
        decision = json.loads(response)
        # 验证决策合法性
        if decision['action'] == 'play_cards':
            if not self.validate_cards(decision['cards']):
                # 如果AI决策不合法，返回默认的pass
                return {'action': 'pass', 'reasoning': 'AI decision invalid, fallback to pass'}
        return decision
    except (json.JSONDecodeError, KeyError):
        return {'action': 'pass', 'reasoning': 'Failed to parse AI response'}
```

### AI性能优化策略

**多级缓存系统**：
- L1缓存：完全相同游戏状态的决策结果
- L2缓存：相似局面的决策模板
- L3缓存：常见牌型组合的权重评估

**成本控制机制**：
```python
class CostController:
    def __init__(self):
        self.daily_budgets = {
            'gpt-4o-mini': 10.0,  # 每日预算10美元
            'claude-haiku': 5.0,
            'deepseek-v3': 2.0
        }
        self.usage_tracker = {}
        
    async def check_budget(self, model: str, estimated_cost: float) -> bool:
        today = datetime.now().date()
        daily_usage = self.usage_tracker.get((today, model), 0)
        
        if daily_usage + estimated_cost > self.daily_budgets[model]:
            # 超出预算，切换到更便宜的模型
            return False
        return True
```

## API设计规范

### WebSocket通信协议

**消息格式标准**：
```javascript
// 客户端发送消息格式
{
    "type": "GAME_ACTION",
    "roomId": "room_123",
    "playerId": "player_456", 
    "timestamp": 1640995200000,
    "data": {
        "action": "PLAY_CARDS",
        "cards": [3, 4, 5, 6, 7]
    },
    "messageId": "msg_789"
}

// 服务器响应格式
{
    "type": "GAME_STATE_UPDATE",
    "roomId": "room_123",
    "timestamp": 1640995201000,
    "data": {
        "gameState": {...},
        "currentPlayer": "player_456",
        "lastMove": {...}
    },
    "messageId": "response_790"
}
```

### REST API端点设计

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class CreateGameRequest(BaseModel):
    player_name: str
    difficulty: str = "medium"  # easy, medium, hard

class GameAction(BaseModel):
    room_id: str
    player_id: str
    action: str
    cards: List[int] = []

@app.post("/api/games/create")
async def create_game(request: CreateGameRequest):
    """创建新游戏房间"""
    room_id = await game_manager.create_room(request.player_name, request.difficulty)
    return {"room_id": room_id, "status": "created"}

@app.get("/api/games/{room_id}")
async def get_game_state(room_id: str):
    """获取游戏状态"""
    state = await game_manager.get_game_state(room_id)
    if not state:
        raise HTTPException(status_code=404, detail="Game not found")
    return state

@app.post("/api/games/{room_id}/join")
async def join_game(room_id: str, player_name: str):
    """加入游戏"""
    success = await game_manager.add_player(room_id, player_name)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot join game")
    return {"status": "joined"}

@app.websocket("/ws/game/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """游戏WebSocket连接"""
    await connection_manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
            await process_game_message(room_id, data, websocket)
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket, room_id)
```

## 数据存储设计

### 数据库架构

**Redis数据结构**：
```python
# 游戏状态存储 - Hash
game:room_123 {
    "state": "playing",
    "players": "[{\"id\": \"p1\", \"cards\": [3,4,5]}, ...]",
    "current_player": "0",
    "last_updated": "1640995200"
}

# 玩家会话管理 - String
session:player_456 "socket_connection_id_789"

# AI决策缓存 - Hash  
ai_cache:state_hash_abc {
    "decision": "{\"action\": \"play_cards\", \"cards\": [7,7]}",
    "timestamp": "1640995200",
    "confidence": "0.85"
}
```

**MongoDB集合设计**：
```javascript
// 游戏记录集合
{
    "_id": ObjectId("..."),
    "roomId": "room_123",
    "players": [
        {
            "id": "player_456",
            "name": "张三",
            "role": "landlord",
            "finalCards": 0,
            "score": 100
        }
    ],
    "gameLog": [
        {
            "turn": 1,
            "player": "player_456",
            "action": "call_landlord",
            "timestamp": "2024-01-01T10:00:00Z"
        },
        {
            "turn": 2,
            "player": "ai_1",
            "action": "play_cards", 
            "cards": [3, 4, 5, 6, 7],
            "aiModel": "gpt-4o-mini",
            "responseTime": 150
        }
    ],
    "duration": 1200,
    "winner": "player_456",
    "createdAt": "2024-01-01T10:00:00Z"
}

// AI决策分析集合
{
    "_id": ObjectId("..."),
    "gameState": {...},
    "aiDecisions": [
        {
            "model": "gpt-4o-mini",
            "decision": {...},
            "reasoning": "基于当前牌型...",
            "confidence": 0.85,
            "responseTime": 120
        }
    ],
    "optimalMove": {...},
    "performanceRating": 8.5
}
```

### 数据一致性策略

```python
class TransactionManager:
    async def execute_game_action(self, room_id: str, player_id: str, action: dict):
        """事务性执行游戏动作"""
        async with self.db.start_session() as session:
            async with session.start_transaction():
                try:
                    # 1. 验证游戏状态
                    current_state = await self.get_game_state(room_id, session)
                    if not self.validate_action(current_state, player_id, action):
                        raise ValueError("Invalid action")
                    
                    # 2. 更新游戏状态
                    new_state = await self.apply_action(current_state, action, session)
                    
                    # 3. 记录游戏日志
                    await self.log_action(room_id, player_id, action, session)
                    
                    # 4. 更新Redis缓存
                    await self.update_cache(room_id, new_state)
                    
                    await session.commit_transaction()
                    return new_state
                    
                except Exception as e:
                    await session.abort_transaction()
                    raise
```

## 系统性能优化

### 并发处理策略

**游戏房间负载均衡**：
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class GameLoadBalancer:
    def __init__(self, worker_count: int = 4):
        self.workers = [GameWorker(i) for i in range(worker_count)]
        self.room_assignments = {}
        
    def assign_room(self, room_id: str) -> GameWorker:
        # 使用哈希算法确保同一房间总是分配到同一worker
        worker_index = hash(room_id) % len(self.workers)
        self.room_assignments[room_id] = worker_index
        return self.workers[worker_index]
        
    async def process_action(self, room_id: str, action: dict):
        worker = self.workers[self.room_assignments[room_id]]
        return await worker.handle_action(room_id, action)

class GameWorker:
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.rooms = {}
        self.ai_executor = ThreadPoolExecutor(max_workers=2)
        
    async def handle_action(self, room_id: str, action: dict):
        if room_id not in self.rooms:
            self.rooms[room_id] = GameRoom(room_id)
        
        room = self.rooms[room_id]
        
        # 如果需要AI决策，使用线程池异步处理
        if action.get('requires_ai'):
            loop = asyncio.get_event_loop()
            ai_decision = await loop.run_in_executor(
                self.ai_executor, 
                self.get_ai_decision, 
                room.get_state()
            )
            action['ai_decision'] = ai_decision
            
        return await room.process_action(action)
```

### 缓存优化策略

```python
class SmartCacheManager:
    def __init__(self):
        self.l1_cache = {}  # 内存缓存
        self.l2_cache = redis.Redis()  # Redis缓存
        
    async def get_ai_decision(self, game_state: dict) -> dict:
        state_hash = self.calculate_state_hash(game_state)
        
        # L1 内存缓存检查
        if state_hash in self.l1_cache:
            return self.l1_cache[state_hash]
            
        # L2 Redis缓存检查
        cached = await self.l2_cache.get(f"ai_decision:{state_hash}")
        if cached:
            decision = json.loads(cached)
            self.l1_cache[state_hash] = decision  # 回写L1
            return decision
            
        # 缓存未命中，调用AI服务
        decision = await self.ai_service.get_decision(game_state)
        
        # 写入两级缓存
        self.l1_cache[state_hash] = decision
        await self.l2_cache.setex(
            f"ai_decision:{state_hash}", 
            1800,  # 30分钟过期
            json.dumps(decision)
        )
        
        return decision
```

## 安全和监控

### 安全防护机制

```python
class SecurityManager:
    def __init__(self):
        self.rate_limiters = {}
        self.suspicious_activities = {}
        
    async def validate_request(self, request: dict, client_ip: str) -> bool:
        # 频率限制检查
        if not await self.check_rate_limit(client_ip):
            return False
            
        # 输入验证
        if not self.validate_input(request):
            return False
            
        # 反作弊检查
        if await self.detect_cheating(request):
            await self.flag_suspicious_activity(client_ip, "POTENTIAL_CHEAT")
            return False
            
        return True
        
    async def detect_cheating(self, request: dict) -> bool:
        """检测作弊行为"""
        player_id = request.get('playerId')
        
        # 检查操作时间是否异常
        if self.is_response_too_fast(player_id, request):
            return True
            
        # 检查决策是否过于完美
        if await self.is_decision_too_perfect(player_id, request):
            return True
            
        return False
```

### 监控系统设计

```python
import logging
import time
from prometheus_client import Counter, Histogram, Gauge

class GameMetrics:
    def __init__(self):
        self.games_created = Counter('games_created_total', 'Total games created')
        self.games_completed = Counter('games_completed_total', 'Total games completed')
        self.ai_response_time = Histogram('ai_response_seconds', 'AI response time')
        self.active_players = Gauge('active_players', 'Currently active players')
        self.error_rate = Counter('errors_total', 'Total errors', ['error_type'])
        
    def record_game_start(self):
        self.games_created.inc()
        
    def record_ai_response(self, response_time: float):
        self.ai_response_time.observe(response_time)
        
    def record_error(self, error_type: str):
        self.error_rate.labels(error_type=error_type).inc()

class AlertManager:
    async def check_system_health(self):
        """系统健康检查"""
        # 检查AI服务响应时间
        if self.metrics.ai_response_time.average() > 5.0:  # 5秒阈值
            await self.send_alert("AI_SLOW_RESPONSE", {
                "average_response_time": self.metrics.ai_response_time.average()
            })
            
        # 检查错误率
        error_rate = self.calculate_error_rate()
        if error_rate > 0.05:  # 5%错误率阈值
            await self.send_alert("HIGH_ERROR_RATE", {
                "error_rate": error_rate
            })
```

## 部署和运维

### Docker容器化部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  game-api:
    build: 
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - MONGODB_URL=mongodb://mongo:27017/doudizhu
      - MYSQL_URL=mysql://user:pass@mysql:3306/doudizhu
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
    depends_on:
      - redis
      - mongo
      - mysql
    restart: unless-stopped
    
  websocket-server:
    build: 
      context: .
      dockerfile: Dockerfile.ws
    ports:
      - "8001:8001"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    
  mongo:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
      
  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: doudizhu
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - game-api
      - websocket-server

volumes:
  redis_data:
  mongo_data:
  mysql_data:
```

### Kubernetes生产部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: doudizhu-game-server
  namespace: games
spec:
  replicas: 3
  selector:
    matchLabels:
      app: doudizhu-game-server
  template:
    metadata:
      labels:
        app: doudizhu-game-server
    spec:
      containers:
      - name: game-server
        image: doudizhu-game:v1.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: doudizhu-secrets
              key: redis-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: doudizhu-service
  namespace: games
spec:
  selector:
    app: doudizhu-game-server
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## 项目实施计划

### 开发阶段规划

**第一阶段（4-6周）- 核心系统搭建**
- 游戏规则引擎开发
- 基础API和数据库设计
- 简单AI对手实现
- 基础前端界面

**第二阶段（3-4周）- AI集成优化**
- 大模型API集成
- 提示词工程优化
- AI决策缓存系统
- 性能监控系统

**第三阶段（2-3周）- 功能完善**
- 用户系统和认证
- 游戏记录和统计
- 安全防护机制
- UI/UX优化

**第四阶段（2-3周）- 测试部署**
- 压力测试和性能优化
- 生产环境部署
- 监控告警系统
- 文档完善

### 预算估算

**开发成本**：
- 后端开发：60-80人天
- 前端开发：40-50人天
- AI集成和优化：30-40人天
- 测试和部署：20-30人天

**运营成本（月度）**：
- 服务器费用：$200-500
- AI API调用费用：$50-200（取决于用户量）
- 域名和SSL证书：$20
- 监控和日志服务：$30-100

### 成功指标定义

**技术指标**：
- 游戏响应延迟 < 200ms (P95)
- AI决策时间 < 5秒 (P99)
- 系统可用性 > 99.5%
- 缓存命中率 > 80%

**业务指标**：
- 单局游戏完成率 > 85%
- 用户会话时长 > 15分钟
- AI决策合理性评分 > 8.0/10
- 用户满意度 > 4.0/5.0

## 技术风险和缓解策略

### 主要风险点

**AI服务稳定性风险**
- 缓解措施：多模型备份、本地AI服务候补、降级策略

**成本控制风险**
- 缓解措施：智能缓存、使用量监控、成本预警、模型降级

**性能扩展风险**
- 缓解措施：微服务架构、水平扩展设计、负载测试

**安全防护风险**
- 缓解措施：多层安全防护、实时监控、自动封禁机制

### 技术选择的权衡

**FastAPI vs Django**：选择FastAPI获得更好的异步性能，但需要自行实现用户管理等功能
**MongoDB vs MySQL**：使用混合存储，发挥各自优势
**多模型 vs 单模型**：多模型提供更好的稳定性和成本控制，但增加了复杂性

这份产品文档为AI斗地主游戏的开发提供了完整的技术方案和实施指南。通过采用现代化的技术架构、智能的AI集成方案以及完善的监控体系，能够构建一个高性能、用户友好的智能卡牌游戏平台。建议按照规划的阶段逐步实施，重点关注AI决策质量和系统性能优化。