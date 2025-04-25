# n8n_tedtalk 📜

打造自動化 TED Talk 字幕整理與英語學習素材生成流程，只要貼上 TED YouTube 網址，即可：

1. 取得逐字稿字幕  
2. 解析影片標題、縮圖  
3. 呼叫 LLM 重整段落、挑選單字  
4. 產出版面清晰的 PDF

> **Workflow**:自動化抓取 TED Talk 字幕 → 重整段落 & 單字 → 產出 PDF 的工作流程  
> **Stack**：n8n · Python · Docker · GitHub Actions（選配）

![架構示意](assets/n8n%20architecture.png)

| 元件 | 角色 | 關鍵技術 / 執行環境 |
|------|------|--------------------|
| **User / Postman** | 透過 Webhook 傳入影片 URL | HTTP POST |
| **n8n** | 工作流程協調中心；觸發 API、LLM、PDF 產生 | n8n (Node.js, Docker) |
| **subtitle-api** | 擷取字幕 + 影片 meta | FastAPI, yt-dlp |
| **PDF Generator** | 把整理後內容轉成排版良好的 PDF | Python + fpdf2 |
| **PDF Folder** | 輸出成果；可掛載到主機 | Volume `/n8n/pdf` |

---

## 🏃‍♀️ 快速開始

```bash
# 1. Clone 專案
git clone https://github.com/Shuhanliu-0925/n8n_tedtalk.git
cd n8n_tedtalk

# 2. 啟動
docker compose up -d

# 3. 進入 Container 
http://localhost:5678    #n8n 編輯畫面
http://localhost:5005    #FlaskAPI

