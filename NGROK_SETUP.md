# StorySpark ngrok Setup

This guide helps you expose StorySpark to the internet using ngrok for external testing and demos.

## Demo Setup (Recommended)

For a **single demoable link** that provides the full StorySpark experience:

```bash
./setup_demo.sh
```

Then follow the instructions to:
1. Start backend: `cd backend && python app.py`
2. Start frontend: `cd frontend && npm run dev` 
3. Expose via ngrok: `ngrok http 5173`

**Result**: One public URL that serves the complete app! 🎉

## Alternative Setups

### Option A: Expose Frontend Only (Best for Demos)

```bash
# Terminal 1: Backend (local)
cd backend && python app.py

# Terminal 2: Frontend (local) 
cd frontend && npm run dev

# Terminal 3: Expose frontend
ngrok http 5173
```

**Demo URL**: `https://your-ngrok-url.ngrok.io` ✅ Complete app experience

**Note**: If you get a "Blocked request" error, restart the frontend server after the Vite config update.

### Option B: Expose Backend Only (API Testing)

```bash
# Terminal 1: Backend + ngrok
cd backend && python app.py
# Terminal 2:
ngrok http 5001
```

**Demo URL**: `https://your-ngrok-url.ngrok.io/api` ⚙️ API endpoints only

## Testing the API

Once ngrok is running, you can test the API directly:

```bash
# Test story generation
curl -X POST https://your-ngrok-url.ngrok.io/api/voice/generate-story \
  -H "Content-Type: application/json" \
  -d '{"theme": "kindness", "setting": "forest", "duration": "short"}'
```

## Frontend with ngrok Backend

If you want the frontend to use the ngrok backend URL instead of localhost:

```bash
# Set environment variable before starting frontend
export VITE_API_BASE_URL="https://your-ngrok-url.ngrok.io/api"
export VITE_STATIC_BASE_URL="https://your-ngrok-url.ngrok.io/static"
cd frontend
npm run dev
```

## Configuration Details

The backend is configured with:
- **Host**: `0.0.0.0` (accepts external connections)
- **Port**: `5001` 
- **CORS**: Enabled for all origins (`*`)
- **Headers**: Permissive for cross-origin requests

## Security Notes

- This configuration is for development/testing only
- In production, restrict CORS origins to specific domains
- Use HTTPS in production environments
