# 📋 Plan Công Việc - Tái Tạo Repo Salary-Agent-Ver2

**Ngày tạo:** 2 Tháng 2, 2026  
**Môi trường:** conda activate salary-ver2  
**Mục tiêu:** Chuyển từ OpenAI GPT sang Google Gemini và hợp nhất chat history classes

---

## 🎯 Tổng Quan Yêu Cầu

### 1. Hợp nhất Chat History Classes
- **File:** `template/agent/histories.py`
- **Vấn đề hiện tại:** Có 2 classes riêng biệt
  - `ImageSupportChatHistory`: Lưu text + image vào JSON file
  - `RedisSupportChatHistory`: Lưu text vào Redis cache
- **Yêu cầu:** Merge thành 1 class có thể:
  - Hỗ trợ cả text và image
  - Lưu trữ vào Redis để cache
  - Tùy chọn storage backend (file hoặc Redis)

### 2. Chuyển sang Google Gemini
- **File:** `template/agent/agent.py`
- **Thay đổi:**
  - Từ: `ChatOpenAI` (OpenAI GPT)
  - Sang: `ChatVertexAI` (Google Gemini)
- **Cấu hình:**
  - Model: `gemini-2.5-flash` (đã có trong env)
  - Authentication: `service-account.json`
  - Project & Location: từ environment variables

### 3. Docker Build & Test
- Build Docker image với cấu hình mới
- Run docker compose để test
- Verify API hoạt động với Gemini

---

## 📝 Chi Tiết Các Bước Thực Hiện

### ✅ Bước 1: Hợp Nhất Chat History Classes
**File:** `template/agent/histories.py`

**Nhiệm vụ:**
- Tạo class mới `RedisSupportChatHistory` kế thừa `BaseChatMessageHistory`
- Tích hợp features từ cả 2 classes cũ:
  - Support text + image content (multimodal)
  - Storage backend: File JSON hoặc Redis
  - TTL support cho Redis
  - Session management utilities
- Parameters:
  - `session_id`: ID của session
  - `user_id`: ID của user  
  - `storage`: "file" hoặc "redis" (default: "redis")
  - `ttl`: Time-to-live cho Redis (default: 3600s)

**Cấu trúc class mới:**
```python
class RedisSupportChatHistory(BaseChatMessageHistory):
    def __init__(self, session_id, user_id, storage="redis", ttl=3600):
        # Khởi tạo với storage backend tùy chọn
    
    def add_user_message(self, message, image_url=None):
        # Thêm message từ user, có thể kèm image
    
    def add_ai_message(self, message):
        # Thêm response từ AI
    
    def clear(self):
        # Xóa toàn bộ history
```

**Lợi ích:**
- Code gọn gàng hơn, không duplicate
- Dễ maintain và extend
- Flexibility trong việc chọn storage

---

### ✅ Bước 2: Cập Nhật Dependencies
**File:** `pyproject.toml`

**Thêm packages:**
```toml
langchain-google-vertexai = "^2.0.0"
google-cloud-aiplatform = "^1.70.0"
```

**Giải thích:**
- `langchain-google-vertexai`: LangChain integration cho Vertex AI (ChatVertexAI)
- `google-cloud-aiplatform`: Google Cloud AI Platform SDK

---

### ✅ Bước 3: Chuyển Agent sang Gemini
**File:** `template/agent/agent.py`

**Thay đổi import:**
```python
# Cũ:
from langchain_openai import ChatOpenAI

# Mới:
from langchain_google_vertexai import ChatVertexAI
```

**Cập nhật Agent initialization:**
```python
# Cũ:
self.llm = ChatOpenAI(
    model=model,
    temperature=0.0,
    api_key=api_key
)

# Mới:
self.llm = ChatVertexAI(
    model=env.MODEL_NAME,  # gemini-2.5-flash
    project=env.GOOGLE_CLOUD_PROJECT,
    location=env.GOOGLE_CLOUD_LOCATION,
    credentials=env.GOOGLE_APPLICATION_CREDENTIALS,
    temperature=0.0
)
```

**Environment Variables cần thiết:**
- `MODEL_NAME`: gemini-2.5-flash
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `GOOGLE_CLOUD_LOCATION`: us-east1
- `GOOGLE_APPLICATION_CREDENTIALS`: service-account.json

---

### ✅ Bước 4: Cập Nhật Dockerfile
**File:** `Dockerfile`

**Đảm bảo:**
1. Service account file được copy vào container
2. Environment variable được set đúng
3. Google Cloud SDK dependencies được cài đặt

**Thay đổi cần thiết:**
```dockerfile
# Copy service account
COPY service-account.json /app/service-account.json

# Set environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json
```

---

### ✅ Bước 5: Build Docker Image
**Commands:**
```bash
# Build image
docker compose build

# Hoặc build riêng service
docker compose build salary-agent-service
```

**Verify:**
- Check build logs không có error
- Confirm các packages được install đúng
- Verify service-account.json có trong image

---

### ✅ Bước 6: Run & Test Application
**Commands:**
```bash
# Start all services
docker compose up -d

# Check logs
docker compose logs -f salary-agent-service

# Check health
curl http://localhost:8000/health
```

**Test API:**
```bash
# Test chat endpoint
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "user_id": 100,
    "message": "Hello, what can you do?"
  }'
```

**Verify:**
- API response thành công
- Agent sử dụng Gemini model
- Redis cache hoạt động
- Chat history được lưu đúng

---

## 🔍 Checklist Kiểm Tra

### Pre-Implementation
- [ ] Backup code hiện tại
- [ ] Đọc và hiểu rõ cấu trúc code
- [ ] Confirm environment variables đầy đủ
- [ ] Verify service-account.json tồn tại

### During Implementation
- [ ] Merge chat history classes thành công
- [ ] Update dependencies không conflict
- [ ] Agent code chuyển sang ChatVertexAI
- [ ] Dockerfile cấu hình credentials đúng

### Post-Implementation
- [ ] Docker build thành công
- [ ] All services start up clean
- [ ] API endpoint accessible
- [ ] Chat functionality works with Gemini
- [ ] Redis caching works properly
- [ ] No errors in logs

---

## ⚠️ Lưu Ý Quan Trọng

### 1. Google Cloud Authentication
- File `service-account.json` phải có đầy đủ permissions
- Service account cần roles:
  - Vertex AI User
  - AI Platform Admin (hoặc tương đương)

### 2. Environment Variables
- Kiểm tra file `.env` có đầy đủ biến:
  - `GOOGLE_CLOUD_PROJECT`
  - `GOOGLE_CLOUD_LOCATION`
  - `GOOGLE_APPLICATION_CREDENTIALS`
  - `MODEL_NAME`

### 3. API Differences
- Gemini API có thể có response format khác GPT
- Cần test kỹ với các loại query khác nhau
- Image handling có thể khác

### 4. Cost Considerations
- Vertex AI có pricing khác OpenAI
- Monitor usage trong GCP Console

---

## 🚀 Tiến Độ Thực Hiện

| Bước | Trạng Thái | Ghi Chú |
|------|-----------|---------|
| 1. Merge Chat History | ⏳ Chờ xác nhận | |
| 2. Update Dependencies | ⏳ Chờ xác nhận | |
| 3. Switch to Gemini | ⏳ Chờ xác nhận | |
| 4. Update Dockerfile | ⏳ Chờ xác nhận | |
| 5. Build Docker | ⏳ Chờ xác nhận | |
| 6. Test Application | ⏳ Chờ xác nhận | |

---

## 📞 Next Steps

**Sau khi bạn xác nhận plan này:**
1. Tôi sẽ bắt đầu implement từng bước
2. Mỗi bước sẽ được test kỹ trước khi chuyển sang bước tiếp
3. Báo cáo progress sau mỗi milestone
4. Final test và handover