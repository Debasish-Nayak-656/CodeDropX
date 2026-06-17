# 🚀 DropZone — Instant File Sharing App

A full-stack file sharing app. Upload any file → get a **6-character code** → share the code → anyone can download instantly. No login required.

---

## 📁 Project Structure

```
dropzone/
├── main.py              # FastAPI backend
├── requirements.txt     # Python dependencies
├── meta.json            # Auto-generated: file metadata store
├── uploads/             # Auto-generated: uploaded files
└── static/
    └── index.html       # Full frontend (Send + Receive UI)
```

---

## ⚙️ Setup & Run

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the server
```bash
python main.py
```

### 3. Open in browser
```
http://localhost:8000
```

---

## 🔌 API Endpoints

| Method | Endpoint            | Description                        |
|--------|---------------------|------------------------------------|
| GET    | `/`                 | Serve the frontend UI              |
| POST   | `/upload`           | Upload a file, returns a code      |
| GET    | `/info/{code}`      | Get file metadata by code          |
| GET    | `/download/{code}`  | Download file by code              |
| GET    | `/stats`            | Active files & total size          |

---

## 📋 How It Works

1. **Sender** uploads a file → server saves it to `uploads/` and generates a unique 6-char code in `meta.json`
2. **Sender** shares the code (WhatsApp, SMS, etc.)
3. **Receiver** enters the code on the Receive tab → sees file preview → clicks Download
4. Files **auto-expire after 24 hours** and are deleted from disk

---

## 🔒 Limits

- Max file size: **100 MB**
- Files expire: **24 hours**
- No authentication required (public access)

---

## 🌐 Deploy to the Internet

To share with people outside your network, deploy to:

- **Railway**: `railway up`
- **Render**: Connect GitHub repo, set start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **VPS (DigitalOcean/Linode)**: Run behind Nginx + Gunicorn

---

## 🛠 Tech Stack

- **Backend**: Python 3.11 + FastAPI + Uvicorn
- **Storage**: Local filesystem (`uploads/`) + JSON metadata
- **Frontend**: Vanilla HTML/CSS/JS (no framework needed)
