# 🎭 StorySpark Demo Guide

## Quick Demo Setup (Single Demoable Link)

### Option 1: Automated Setup (Recommended)

```bash
./start_demo.sh
```

This will:
- ✅ Start backend on http://localhost:5001
- ✅ Start frontend on http://localhost:5173  
- ✅ Show you the ngrok command to run

Then in **another terminal**:
```bash
ngrok http 5173
```

**Your demo URL**: The HTTPS URL that ngrok provides! 🌐

### If you get "Blocked request" error:

The frontend is now configured to allow all ngrok hosts, but if you started the frontend before the fix:

1. **Stop the frontend** (Ctrl+C)
2. **Restart it**: `cd frontend && npm run dev`
3. **Expose via ngrok**: `ngrok http 5173`

### Option 2: Manual Setup

```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend  
cd frontend
npm run dev

# Terminal 3: Expose via ngrok
ngrok http 5173
```

## What You Get

- **Single Public URL**: `https://xxxxx.ngrok.io`
- **Full App Experience**: Complete StorySpark interface
- **Real Story Generation**: Powered by Google Gemini API
- **Real Audio**: Google Cloud Text-to-Speech 
- **Mobile Friendly**: Works on phones/tablets

## Demo Features

✅ Generate personalized stories
✅ Play AI-generated audio narration  
✅ Multiple story themes and settings
✅ Kid-friendly interface
✅ PWA features (can be "installed")

## What Happens Behind the Scenes

1. **User visits ngrok URL** → Frontend served
2. **User generates story** → Frontend proxies to local backend
3. **Backend calls Gemini API** → Story generated
4. **Backend calls Google TTS** → Audio created
5. **User gets complete story** → With text + audio

## Technical Details

- **Frontend**: React + Vite (port 5173)
- **Backend**: Flask (port 5001) 
- **Proxy**: Frontend proxies `/api` and `/static` to backend
- **ngrok**: Exposes frontend, backend stays local
- **CORS**: Configured for external access

## For Testers

Send them just the ngrok URL - they get the full experience! No setup required on their end.

## Stopping the Demo

Press `Ctrl+C` in the terminal running `start_demo.sh` to stop all services.
