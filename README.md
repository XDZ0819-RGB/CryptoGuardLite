# CryptoGuardLite

基于深度学习的加密流量入侵检测系统

## 项目简介

CryptoGuardLite 是一个基于深度学习的加密流量入侵检测系统，采用 CNN-BiLSTM-Transformer 混合模型进行加密流量分析，能够检测多种网络攻击类型。

### 主要特性

- 🔒 **加密流量分析**：无需解密即可分析加密流量特征
- 🧠 **混合深度学习模型**：结合 CNN、BiLSTM 和 Transformer 的优势
- 🎯 **多类型攻击检测**：支持 DDoS、C2、挖矿、端口扫描等多种攻击检测
- 🚀 **RESTful API**：提供易用的 API 接口进行实时检测
- 📊 **可视化界面**：支持前端可视化展示检测结果
- 🐳 **容器化部署**：支持 Docker 快速部署

## 项目结构

```
CryptoGuardLite/
├── src/                          # 源代码目录
│   ├── api/                      # API 服务
│   │   ├── main.py              # FastAPI 主程序
│   │   └── __init__.py
│   ├── data_processing/          # 数据处理模块
│   │   ├── dataset.py           # 数据集加载器
│   │   └── __init__.py
│   ├── feature_extraction/       # 特征提取模块
│   │   ├── traffic_extractor.py # 流量特征提取器
│   │   └── __init__.py
│   ├── models/                   # 模型定义
│   │   ├── baseline/            # 基线模型（CNN）
│   │   │   ├── cnn_model.py
│   │   │   └── __init__.py
│   │   ├── hybrid/              # 混合模型
│   │   │   ├── hybrid_model.py
│   │   │   └── __init__.py
│   │   ├── trainer.py           # 模型训练器
│   │   └── __init__.py
│   ├── utils/                    # 工具模块
│   │   ├── config.py            # 配置管理
│   │   ├── logger.py            # 日志管理
│   │   └── __init__.py
│   └── frontend/                 # 前端代码（预留）
├── tests/                        # 测试代码
│   ├── unit/                    # 单元测试
│   │   ├── test_config.py
│   │   ├── test_feature_extraction.py
│   │   └── test_models.py
│   └── integration/             # 集成测试
├── scripts/                      # 脚本目录
│   ├── train.py                 # 训练脚本
│   ├── predict.py               # 预测脚本
│   └── preprocess.py            # 数据预处理脚本
├── config/                       # 配置文件
│   └── config.yaml              # 主配置文件
├── data/                         # 数据目录
│   ├── raw/                     # 原始数据
│   ├── processed/               # 处理后的数据
│   └── models/                  # 训练好的模型
├── notebooks/                    # Jupyter Notebooks
├── logs/                         # 日志文件
├── main.py                       # 主入口程序
├── requirements.txt              # Python 依赖
├── setup.py                      # 安装配置
├── Dockerfile                    # Docker 配置
├── docker-compose.yml            # Docker Compose 配置
├── Makefile                      # Make 命令
├── setup.sh                      # 环境设置脚本
└── README.md                     # 项目说明

```

## 快速开始

### 环境要求

- Python 3.8+
- CUDA 11.0+ (GPU 训练，可选)
- Docker (容器化部署，可选)

### 安装步骤

#### 方法 1：使用 setup.sh 脚本

```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

#### 方法 2：手动安装

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置 PYTHONPATH
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# 创建必要的目录
mkdir -p data/raw data/processed data/models logs
```

#### 方法 3：使用 Docker

```bash
# 构建镜像
docker build -t cryptoguardlite:latest .

# 运行容器
docker-compose up -d
```

### 使用 Makefile

```bash
# 查看所有命令
make help

# 设置环境
make setup

# 运行 API 服务
make run-api

# 训练模型
make train

# 运行测试
make test
```

## 使用指南

### 1. 数据预处理

```bash
# 预处理 PCAP 文件
python scripts/preprocess.py data/raw/your_data.pcap --output processed_data.npz

# 预处理整个目录
python scripts/preprocess.py data/raw/ --output processed_data.npz
```

### 2. 模型训练

```bash
# 训练混合模型
python scripts/train.py --model hybrid --epochs 50 --batch-size 64

# 训练基线模型
python scripts/train.py --model baseline --epochs 50 --batch-size 32
```

### 3. 启动 API 服务

```bash
# 使用主程序启动
python main.py api

# 直接启动
cd src && uvicorn api.main:app --host 0.0.0.0 --port 8000
```

API 服务将在 `http://localhost:8000` 启动。

访问 API 文档：`http://localhost:8000/docs`

### 4. 使用 API 进行检测

#### 健康检查

```bash
curl http://localhost:8000/health
```

#### 上传 PCAP 文件进行检测

```bash
curl -X POST "http://localhost:8000/predict/pcap" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@traffic.pcap"
```

#### 使用特征进行检测

```bash
curl -X POST "http://localhost:8000/predict/features" \
  -H "Content-Type: application/json" \
  -d '{"features": [[...]]}'
```

### 5. 进行预测

```bash
python scripts/predict.py data/raw/test_traffic.pcap --model hybrid
```

## 支持的攻击类型

系统支持检测以下攻击类型：

1. **Normal** - 正常流量
2. **DDoS** - 分布式拒绝服务攻击
3. **C2** - 命令与控制通信
4. **Mining** - 加密货币挖矿
5. **Port Scan** - 端口扫描
6. **Brute Force** - 暴力破解
7. **SQL Injection** - SQL 注入
8. **XSS** - 跨站脚本攻击
9. **Malware** - 恶意软件
10. **Exfiltration** - 数据窃取

## 配置说明

配置文件位于 `config/config.yaml`，包含以下主要配置：

- **data**: 数据路径配置
- **feature_extraction**: 特征提取参数
- **model**: 模型架构参数
- **training**: 训练超参数
- **api**: API 服务配置

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行单元测试
pytest tests/unit/ -v

# 运行测试并生成覆盖率报告
pytest tests/ -v --cov=src --cov-report=html
```

## 开发计划

### 阶段一：准备与调研 (2025.12 - 2026.1) ✅

- [x] 项目框架搭建
- [x] 开发环境配置
- [ ] 数据集收集与预处理
- [ ] 技术方案详细设计

### 阶段二：模型研发与训练 (2026.2 - 2026.6)

- [x] 特征提取模块开发
- [x] 基线模型实现（CNN）
- [x] 混合模型实现（CNN-BiLSTM-Transformer）
- [ ] 模型训练与调优
- [ ] 模型评估

### 阶段三：系统集成与开发 (2026.7 - 2026.9)

- [x] 后端 API 开发（FastAPI）
- [ ] 前端界面开发
- [ ] 系统联调
- [ ] 性能优化

### 阶段四：测试与成果整理 (2026.10 - 2026.12)

- [x] 单元测试框架
- [ ] 功能测试
- [ ] 性能测试
- [ ] 文档整理
- [ ] 软著申请

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 技术栈

- **深度学习框架**: PyTorch, TensorFlow
- **后端框架**: FastAPI, Uvicorn
- **数据处理**: NumPy, Pandas, Scikit-learn
- **流量分析**: Scapy, dpkt
- **容器化**: Docker, Docker Compose
- **测试**: Pytest
- **日志**: Loguru

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue: [GitHub Issues](https://github.com/XDZ0819-RGB/CryptoGuardLite/issues)
- 项目主页: [GitHub Repository](https://github.com/XDZ0819-RGB/CryptoGuardLite)

## 致谢

感谢所有为本项目做出贡献的开发者和研究人员。

---

**注意**: 本项目仅供学习和研究使用，请勿用于非法用途。
