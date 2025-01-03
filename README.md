# When I Miss Her

A personal web application for privately logging moments when you think about someone special. The app features a pin-protected login system with two access levels:
- Your PIN: Full access to add, edit, and manage entries
- Her PIN: Read-only access to view all entries

## Tech Stack

### Frontend
- React.js
- Material-UI
- React Router
- Axios

### Backend
- FastAPI
- SQLite
- SQLAlchemy
- Python 3.11+

## Project Structure
```
.
├── backend/
│   ├── requirements.txt
│   └── main.py
└── frontend/
    ├── package.json
    └── src/
        ├── components/
        │   ├── PinScreen.js
        │   ├── Dashboard.js
        │   └── ViewerPage.js
        ├── services/
        │   └── api.js
        ├── App.js
        └── index.js
```

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm start
   ```

## Default PINs
- Your PIN: 1234
- Her PIN: 5678

*Note: For security reasons, please change these PINs in production.*

## Features
- Pin-protected access
- Add, edit, and delete entries (your access)
- Read-only view of all entries (her access)
- Responsive design
- Dark mode UI
- Timestamp for each entry

## Security Considerations
- PINs should be stored securely (hashed) in production
- Use environment variables for sensitive data
- Implement rate limiting for PIN attempts
- Use HTTPS in production
- Consider adding session management

## License
MIT License 