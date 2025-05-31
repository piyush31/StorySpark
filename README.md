# StorySpark

StorySpark is a full-stack Progressive Web App (PWA) for interactive storytelling. It features a Python Flask backend API and a React frontend with offline capabilities.

## Project Structure

```
StorySpark/
├── backend/           # Flask API
│   ├── app.py         # Main Flask application
│   ├── requirements.txt
│   ├── models/        # Database models
│   ├── routes/        # API routes
│   └── services/      # Business logic services
├── frontend/          # React PWA
│   ├── public/        # Static assets
│   ├── src/           # React components
│   ├── index.html     # HTML entry point
│   └── vite.config.js # Vite configuration
```

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the Flask app:
   ```
   python app.py
   ```
   The API will be available at http://localhost:5000

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```
   The app will be available at http://localhost:3000

## PWA Features

- Offline access to previously loaded stories
- Installable on supported devices
- Responsive design for mobile and desktop

## API Endpoints

- `GET /api/stories`: Get all available stories
- More endpoints coming soon!

## Technologies Used

- **Backend**: Flask, Python
- **Frontend**: React, Vite
- **PWA**: Workbox, Vite PWA Plugin
