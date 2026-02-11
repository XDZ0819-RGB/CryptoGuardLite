# CryptoGuardLite 项目结构详解

## 目录树

```
CryptoGuardLite/
│
├── 📋 配置和文档文件
│   ├── README.md                    # 项目说明文档
│   ├── FRAMEWORK_SUMMARY.md         # 框架搭建总结
│   ├── PROJECT_STRUCTURE.md         # 本文件
│   ├── LICENSE                      # MIT 许可证
│   ├── requirements.txt             # Python 依赖
│   ├── setup.py                     # 安装配置
│   ├── pytest.ini                   # pytest 配置
│   └── .flake8                      # 代码风格配置
│
├── 🐳 部署相关
│   ├── Dockerfile                   # Docker 镜像
│   ├── docker-compose.yml           # 容器编排
│   ├── Makefile                     # 快捷命令
│   └── setup.sh                     # 环境设置脚本
│
├── ⚙️ config/                        # 配置目录
│   └── config.yaml                  # 主配置文件
│
├── 💾 data/                          # 数据目录
│   ├── raw/                         # 原始数据（PCAP文件等）
│   ├── processed/                   # 处理后的数据
│   └── models/                      # 训练好的模型
│
├── 📝 docs/                          # 文档目录
│   ├── DEVELOPMENT.md               # 开发指南
│   └── API.md                       # API 使用文档
│
├── 📊 notebooks/                     # Jupyter Notebooks
│   └── quick_start.ipynb            # 快速开始教程
│
├── 🔧 scripts/                       # 脚本目录
│   ├── __init__.py
│   ├── train.py                     # 训练脚本
│   ├── predict.py                   # 预测脚本
│   └── preprocess.py                # 数据预处理脚本
│
├── 🧪 tests/                         # 测试目录
│   ├── unit/                        # 单元测试
│   │   ├── test_config.py           # 配置测试
│   │   ├── test_models.py           # 模型测试
│   │   └── test_feature_extraction.py # 特征提取测试
│   └── integration/                 # 集成测试
│       └── __init__.py
│
├── 📦 src/                           # 源代码目录
│   ├── __init__.py
│   │
│   ├── 🔍 feature_extraction/        # 特征提取模块
│   │   ├── __init__.py
│   │   └── traffic_extractor.py     # 流量特征提取器
│   │
│   ├── 🗃️ data_processing/           # 数据处理模块
│   │   ├── __init__.py
│   │   └── dataset.py               # 数据集加载器
│   │
│   ├── �� models/                    # 模型模块
│   │   ├── __init__.py
│   │   ├── trainer.py               # 模型训练器
│   │   ├── baseline/                # 基线模型
│   │   │   ├── __init__.py
│   │   │   └── cnn_model.py         # CNN 模型
│   │   └── hybrid/                  # 混合模型
│   │       ├── __init__.py
│   │       └── hybrid_model.py      # CNN-BiLSTM-Transformer
│   │
│   ├── 🌐 api/                       # API 服务
│   │   ├── __init__.py
│   │   └── main.py                  # FastAPI 应用
│   │
│   ├── 🎨 frontend/                  # 前端（预留）
│   │
│   └── 🛠️ utils/                     # 工具模块
│       ├── __init__.py
│       ├── config.py                # 配置管理
│       └── logger.py                # 日志管理
│
├── 📋 main.py                        # 主入口程序
└── 📄 logs/                          # 日志文件目录

```

## 模块功能说明

### 1. 特征提取模块 (feature_extraction)
**功能**: 从网络流量中提取特征用于模型训练和推理

**主要类**:
- `TrafficFeatureExtractor`: 流量特征提取器
  - 读取 PCAP 文件
  - 提取包级特征（长度、协议、标志位等）
  - 提取流级特征（统计特征）
  - 生成时序特征序列

**输入**: PCAP 文件或数据包列表
**输出**: 特征向量数组

### 2. 数据处理模块 (data_processing)
**功能**: 数据加载、预处理和批处理

**主要类**:
- `TrafficDataset`: PyTorch 数据集类
- `DataProcessor`: 数据处理类
  - 数据加载
  - 特征归一化
  - 训练/测试集划分
  - DataLoader 创建

**输入**: 原始特征和标签
**输出**: PyTorch DataLoader

### 3. 模型模块 (models)
**功能**: 深度学习模型定义、训练和推理

#### 3.1 基线模型 (baseline)
- `BaselineCNN`: 简单的卷积神经网络
  - 3层卷积 + 池化
  - 批归一化
  - 全连接分类层

#### 3.2 混合模型 (hybrid)
- `HybridModel`: CNN-BiLSTM-Transformer 混合架构
  - **CNN 层**: 提取局部特征
  - **BiLSTM 层**: 建模时序依赖
  - **Transformer 层**: 捕获长距离依赖
  - **注意力机制**: 加权池化

#### 3.3 训练器
- `ModelTrainer`: 统一的训练接口
  - 训练循环
  - 验证
  - 早停
  - 模型保存/加载

**输入**: 特征数组 (batch_size, sequence_length, feature_dim)
**输出**: 分类logits (batch_size, num_classes)

### 4. API 模块 (api)
**功能**: 提供 RESTful API 接口

**主要端点**:
- `GET /health`: 健康检查
- `POST /predict/pcap`: PCAP 文件检测
- `POST /predict/features`: 特征向量检测
- `GET /model/info`: 模型信息

**技术栈**: FastAPI + Uvicorn

### 5. 工具模块 (utils)
**功能**: 通用工具和辅助函数

**主要组件**:
- `Config`: 配置管理（YAML）
- `Logger`: 日志管理（loguru）

### 6. 脚本 (scripts)
**功能**: 命令行工具

**主要脚本**:
- `train.py`: 模型训练
- `predict.py`: 预测
- `preprocess.py`: 数据预处理

## 数据流

```
原始流量 (PCAP)
    ↓
[TrafficFeatureExtractor]
    ↓
特征向量
    ↓
[DataProcessor]
    ↓
PyTorch DataLoader
    ↓
[Model (CNN/Hybrid)]
    ↓
预测结果
    ↓
[API/前端]
    ↓
用户
```

## 训练流程

```
1. 数据准备
   - 收集 PCAP 文件
   - 标注攻击类型
   
2. 特征提取
   python scripts/preprocess.py data/raw/ --output processed_data.npz
   
3. 模型训练
   python scripts/train.py --model hybrid --epochs 50
   
4. 模型评估
   - 查看训练日志
   - 评估测试集性能
   
5. 模型部署
   - 保存最佳模型
   - 启动 API 服务
```

## 推理流程

```
1. 启动 API
   python main.py api
   
2. 上传流量
   curl -X POST http://localhost:8000/predict/pcap \
     -F "file=@traffic.pcap"
   
3. 获取结果
   {
     "prediction": "DDoS",
     "confidence": 0.92,
     "probabilities": {...}
   }
```

## 开发工作流

```
1. 设置环境
   ./setup.sh
   source venv/bin/activate
   
2. 开发功能
   - 编写代码
   - 编写测试
   
3. 运行测试
   pytest tests/unit/ -v
   
4. 代码风格检查
   flake8 src/
   black src/
   
5. 提交代码
   git commit -m "feat: xxx"
   git push
```

## 配置文件说明

### config/config.yaml
```yaml
# 数据配置
data:
  raw_data_dir: "data/raw"        # 原始数据目录
  processed_data_dir: "data/processed"  # 处理后数据目录
  model_dir: "data/models"        # 模型保存目录

# 特征提取配置
feature_extraction:
  max_packet_length: 1500         # 最大包长
  sequence_length: 100            # 序列长度

# 模型配置
model:
  baseline:
    type: "CNN"
    epochs: 50
  hybrid:
    type: "CNN-BiLSTM-Transformer"
    cnn_filters: [64, 128, 256]
    lstm_hidden_size: 128
    transformer_heads: 8
    epochs: 100

# API 配置
api:
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["http://localhost:3000"]
```

## 扩展性

### 添加新的攻击类型
1. 修改 `config/config.yaml` 中的 `attack_types`
2. 重新训练模型

### 添加新的特征
1. 在 `TrafficFeatureExtractor` 中添加特征提取逻辑
2. 更新模型输入维度
3. 重新训练

### 添加新的模型
1. 在 `src/models/` 下创建新模型文件
2. 继承 `nn.Module`
3. 在训练脚本中添加模型选项

## 性能优化建议

1. **数据加载**: 使用多进程 DataLoader
2. **模型训练**: 使用混合精度训练
3. **推理**: 模型量化、批处理
4. **API**: 异步处理、缓存

## 常见问题

### Q: 如何添加自定义数据集?
A: 将 PCAP 文件放入 `data/raw/`，运行预处理脚本

### Q: 如何修改模型超参数?
A: 编辑 `config/config.yaml` 或命令行参数

### Q: 如何部署到生产环境?
A: 使用 Docker: `docker-compose up -d`

---

更多信息请查看 README.md 和各模块的文档字符串。
