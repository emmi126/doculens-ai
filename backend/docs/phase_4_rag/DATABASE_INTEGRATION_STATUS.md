# 数据库集成测试状态报告

**日期**: 2025-12-06
**状态**: 🟡 需要手动完成 pgvector 安装

---

## ✅ 已完成的步骤

| 步骤 | 状态 | 详情 |
|------|------|------|
| PostgreSQL 14 安装 | ✅ | Homebrew 安装成功 |
| PostgreSQL 服务启动 | ✅ | 已启动并运行 |
| 数据库创建 | ✅ | `doculens` 数据库已创建 |
| 用户创建 | ✅ | 用户 `doculens` 已创建，密码: `password` |
| 初始 schema 迁移 | ✅ | users, courses, documents 表已创建 |
| pgvector 源码下载 | ✅ | v0.8.1 已下载到 `/tmp/pgvector` |
| pgvector 编译 | ✅ | 编译成功 |
| pgvector 安装 | ⏳ | **需要 sudo 密码** |

---

## 🔧 需要手动执行的命令

### 方案 A: 完成 pgvector 安装（推荐）

```bash
# 1. 打开终端，导航到项目目录
cd /Users/marcochen/code/doculens-ai/backend

# 2. 设置环境变量
export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"
export PG_CONFIG=/opt/homebrew/opt/postgresql@14/bin/pg_config

# 3. 安装 pgvector（需要输入 sudo 密码）
cd /tmp/pgvector
sudo make install

# 4. 验证安装
ls /opt/homebrew/share/postgresql@14/extension/vector*

# 5. 重启 PostgreSQL
brew services restart postgresql@14

# 6. 返回项目目录并运行迁移
cd /Users/marcochen/code/doculens-ai/backend
/opt/homebrew/opt/postgresql@14/bin/psql postgresql://doculens:password@localhost:5432/doculens -f migrations/002_add_vector_embeddings.sql

# 7. 验证 pgvector
/opt/homebrew/opt/postgresql@14/bin/psql postgresql://doculens:password@localhost:5432/doculens -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

### 方案 B: 使用 Docker（如果有 Docker Desktop）

```bash
# 1. 安装 Docker Desktop (如果未安装)
# 下载: https://www.docker.com/products/docker-desktop/

# 2. 启动 PostgreSQL + pgvector 容器
cd /Users/marcochen/code/doculens-ai/backend
docker-compose up -d

# 3. 等待容器启动
sleep 5

# 4. 运行迁移
docker exec -i doculens-postgres psql -U doculens -d doculens < migrations/001_initial_schema.sql
docker exec -i doculens-postgres psql -U doculens -d doculens < migrations/002_add_vector_embeddings.sql

# 5. 验证
docker exec doculens-postgres psql -U doculens -d doculens -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

---

## 🧪 验证步骤（在安装 pgvector 后执行）

### 1. 验证 pgvector 扩展

```bash
cd /Users/marcochen/code/doculens-ai/backend

/opt/homebrew/opt/postgresql@14/bin/psql postgresql://doculens:password@localhost:5432/doculens << 'EOF'
-- 检查扩展
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- 检查 embedding 列
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'documents' AND column_name = 'embedding';

-- 检查索引
SELECT indexname FROM pg_indexes WHERE tablename = 'documents' AND indexname LIKE '%embedding%';
EOF
```

**预期输出**:
```
 extname | extversion
---------+------------
 vector  | 0.8.1

 column_name | data_type
-------------+-----------
 embedding   | USER-DEFINED

 indexname
-------------------------
 documents_embedding_idx
```

### 2. 运行完整测试套件

```bash
cd /Users/marcochen/code/doculens-ai/backend
source venv/bin/activate

# 运行 RAG 系统测试
python scripts/test_rag_setup.py
```

**预期输出**:
```
TEST 1: pgvector Extension          ✓ PASS
TEST 2: Embedding Service            ✓ PASS
TEST 3: Vector Similarity Search     ✓ PASS
TEST 4: RAG Formatting               ✓ PASS

✓ All tests passed! RAG system is ready.
```

### 3. 测试向量操作

```bash
source venv/bin/activate
python << 'EOF'
from database import SessionLocal
from models.document import Document
from services.embedding_service import get_embedding_service
import uuid

# 创建测试文档
db = SessionLocal()
service = get_embedding_service()

# 创建一个带 embedding 的测试文档
test_doc = Document(
    id=uuid.uuid4(),
    course_id=uuid.uuid4(),  # 临时 UUID
    user_id=uuid.uuid4(),    # 临时 UUID
    title="Test Document",
    original_text="This is a test",
    formatted_note="# Test\n\nThis is a test document",
    embedding=service.create_embedding("This is a test document")
)

db.add(test_doc)
db.commit()

print(f"✓ Test document created with ID: {test_doc.id}")
print(f"✓ Embedding dimension: {len(test_doc.embedding)}")

# 清理
db.delete(test_doc)
db.commit()
db.close()

print("✓ Vector operations working!")
EOF
```

---

## 📊 当前数据库状态

### 已创建的表

```sql
✓ users (8 columns)
✓ courses (9 columns)
✓ documents (13 columns + embedding)
```

### 已创建的索引

```sql
✓ users_auth0_user_id_idx
✓ users_email_idx
✓ courses_user_id_idx
✓ documents_course_id_idx
✓ documents_user_id_idx
✓ documents_embedding_idx (HNSW) -- 待安装 pgvector 后创建
```

### 数据库连接信息

```
Host: localhost
Port: 5432
Database: doculens
User: doculens
Password: password
Connection String: postgresql://doculens:password@localhost:5432/doculens
```

---

## 🚀 完成 pgvector 安装后的下一步

### 1. 启动后端服务器

```bash
cd /Users/marcochen/code/doculens-ai/backend
source venv/bin/activate
python main.py
```

或使用 uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 测试 API 端点

```bash
# 健康检查
curl http://localhost:8000/

# 测试 (需要 Auth0 token)
curl -X GET "http://localhost:8000/api/documents/{doc_id}/related?top_k=5" \
  -H "Authorization: Bearer {your_token}"
```

### 3. 如果有现有文档，索引它们

```bash
python scripts/index_existing_notes.py --batch-size 10
```

---

## ⚠️ 故障排除

### 问题 1: pgvector 安装失败

```bash
# 检查编译错误
cd /tmp/pgvector
make clean
make PG_CONFIG=/opt/homebrew/opt/postgresql@14/bin/pg_config

# 检查 PostgreSQL 版本
/opt/homebrew/opt/postgresql@14/bin/psql --version
```

### 问题 2: 扩展找不到

```bash
# 检查扩展文件位置
ls -la /opt/homebrew/share/postgresql@14/extension/vector*
ls -la /opt/homebrew/lib/postgresql@14/vector.so

# 检查 PostgreSQL 配置
/opt/homebrew/opt/postgresql@14/bin/pg_config --sharedir
/opt/homebrew/opt/postgresql@14/bin/pg_config --pkglibdir
```

### 问题 3: 数据库连接失败

```bash
# 检查 PostgreSQL 是否运行
brew services list | grep postgresql

# 重启 PostgreSQL
brew services restart postgresql@14

# 测试连接
/opt/homebrew/opt/postgresql@14/bin/psql postgresql://doculens:password@localhost:5432/doculens -c "SELECT 1;"
```

---

## 📝 当前限制

1. **pgvector 未安装**: 需要 sudo 密码手动完成
2. **向量搜索不可用**: 需要先安装 pgvector
3. **HNSW 索引未创建**: 依赖 pgvector 扩展

---

## ✅ 已验证的功能（无需数据库）

- ✅ Python 代码语法
- ✅ 所有依赖包安装
- ✅ Embedding 服务 (384 维向量生成)
- ✅ Vector Store 服务方法
- ✅ Document 模型定义
- ✅ LLM RAG 方法
- ✅ API 路由集成
- ✅ SQL 迁移文件语法

---

## 🎯 总结

**当前状态**: 数据库已创建并运行，只差最后一步 pgvector 安装。

**需要做的**:
1. 运行方案 A 中的命令（需要输入 sudo 密码一次）
2. 或者安装 Docker Desktop 并使用方案 B

**预计时间**:
- 方案 A: 2-3 分钟（如果 pgvector 已编译）
- 方案 B: 5-10 分钟（包括下载 Docker 镜像）

完成后即可进行完整的 RAG 系统集成测试！

---

**下次运行**:
```bash
cd /Users/marcochen/code/doculens-ai/backend
source venv/bin/activate
python scripts/test_rag_setup.py
```
