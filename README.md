# Video Chat for YouTube

Ask questions about the YouTube video currently playing. Version 1 works with videos that have captions.

## 1. Start the backend

In PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and add your new `GEMINI_API_KEY`, then run:

```powershell
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/health`; it should return `{"status":"ok"}`.

## 2. Install the Chrome extension

1. Open `chrome://extensions`.
2. Turn on **Developer mode**.
3. Select **Load unpacked**.
4. Choose the `extension` folder in this project.
5. Open a captioned YouTube video and select the Video Chat extension icon.

## Notes

- Never put your Gemini API key in the extension.
- The first question for a video downloads its captions and builds a local TF-IDF search index. The index resets when the backend restarts.
- This initial release supports standard YouTube videos, Shorts, and youtube links with captions.
