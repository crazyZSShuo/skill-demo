# RAGFlow v0.24.0 本地部署指南

> 版本：v0.24.0 | 部署方式：Docker Compose | 更新日期：2026-01-15

---

## 功能概述

RAGFlow 是一个开源的检索增强生成（RAG）平台，提供文档解析、知识库管理、对话 API 和可视化工作流编排能力。本指南覆盖从零开始的完整本地部署流程，目标环境为 Linux 裸机或云服务器。

---

## 环境要求

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 操作系统 | Ubuntu 20.04 | Ubuntu 22.04 LTS |
| CPU | 4 核 | 8 核+ |
| 内存 | 16 GB | 32 GB |
| 磁盘 | 50 GB | 200 GB SSD |
| Docker | 24.0+ | 最新稳定版 |
| Docker Compose | v2.20+ | 最新稳定版 |

> **注意**：RAGFlow 内置的文档解析服务（DeepDoc）在 16 GB 内存以下的环境中可能出现 OOM，建议生产部署使用 32 GB 以上。

---

## 部署前准备

### 安装 Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

### 克隆仓库

```bash
git clone https://github.com/infiniflow/ragflow.git
cd ragflow/docker
```

### 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，重点配置以下字段：

```env
# LLM 服务（以 DeepSeek 为例）
LLM_FACTORY=DeepSeek
DEEPSEEK_API_KEY=<your-deepseek-api-key>

# 嵌入模型（以 Jina 为例）
EMBEDDING_FACTORY=Jina
JINA_API_KEY=<your-jina-api-key>

# 服务端口（默认 80）
RAGFLOW_PORT=80
```

---

## 启动服务

```bash
docker compose -f docker-compose.yml up -d
```

首次启动需拉取镜像，约需 5-10 分钟，取决于网络状况。

### 验证服务状态

```bash
docker compose ps
```

正常状态下所有容器应处于 `running`：

```text
NAME                        STATUS          PORTS
ragflow-ragflow-1           running         0.0.0.0:80->80/tcp
ragflow-elasticsearch-1     running         9200/tcp
ragflow-minio-1             running         9000/tcp
ragflow-mysql-1             running         3306/tcp
ragflow-redis-1             running         6379/tcp
```

### 查看启动日志

```bash
docker compose logs -f ragflow
```

出现以下输出表示服务就绪：

```text
 * Running on http://0.0.0.0:9380
```

---

## 访问服务

| 服务 | 地址 |
|------|------|
| Web UI | http://localhost:80 |
| API 文档 | http://localhost:80/v1/api/docs |

首次访问需注册管理员账号。

---

## 配置 LLM 与嵌入模型

进入 **设置 → 模型提供商**，添加对应平台的 API Key。

推荐组合（兼顾成本与效果）：

| 角色 | 推荐选型 |
|------|----------|
| 对话模型 | DeepSeek-V3 |
| 嵌入模型 | BAAI/bge-m3（本地）或 Jina Embeddings v3 |
| 重排序模型 | BAAI/bge-reranker-v2-m3 |

---

## 升级

```bash
git pull origin main
docker compose pull
docker compose up -d
```

> **注意**：跨版本升级前请备份 MySQL 数据，部分版本包含数据库 Schema 变更。

---

## 故障排查

### Web UI 无法访问

检查 80 端口是否被系统防火墙拦截：

```bash
sudo ufw status
sudo ufw allow 80/tcp
```

### Elasticsearch 启动失败

通常由 `vm.max_map_count` 参数不足导致：

```bash
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### 文档解析卡住或失败

查看 task worker 日志：

```bash
docker compose logs -f task_executor
```

若出现内存不足错误，考虑在 `.env` 中禁用高内存消耗的解析功能，或升级服务器内存。

---

## 相关文档

- [RAGFlow 官方文档](https://ragflow.io/docs)
- [架构说明](./RAGFlow架构说明.md)
- [API 参考](https://ragflow.io/docs/dev/http_api_reference)
