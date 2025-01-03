from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from typing import List

app = FastAPI(title="When I Miss Her API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
def get_db():
    db = sqlite3.connect('journal.db')
    try:
        yield db
    finally:
        db.close()

# Initialize database and tables
def init_db():
    db = sqlite3.connect('journal.db')
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        author TEXT NOT NULL
    )''')
    
    # Add pins table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pins (
        role TEXT PRIMARY KEY,
        pin TEXT NOT NULL
    )''')
    
    # Insert default pins if not exist
    cursor.execute('INSERT OR IGNORE INTO pins (role, pin) VALUES (?, ?)', ('you', '6278'))
    cursor.execute('INSERT OR IGNORE INTO pins (role, pin) VALUES (?, ?)', ('her', '1234'))
    
    db.commit()
    db.close()

init_db()

# Models
class PinInput(BaseModel):
    pin: str

class PinChange(BaseModel):
    old_pin: str
    new_pin: str

class JournalEntry(BaseModel):
    content: str
    author: str = "you"

class JournalEntryResponse(BaseModel):
    id: int
    content: str
    created_at: str
    author: str

def get_pin_data(db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute('SELECT role, pin FROM pins')
    return {pin: role for role, pin in cursor.fetchall()}

@app.post("/verify-pin")
async def verify_pin(pin_data: PinInput, db: sqlite3.Connection = Depends(get_db)):
    pin = pin_data.pin
    pin_data = get_pin_data(db)
    if pin in pin_data:
        return {"role": pin_data[pin]}
    raise HTTPException(status_code=401, detail="Invalid PIN")

@app.post("/change-pin")
async def change_pin(pin_data: PinChange, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    pin_dict = get_pin_data(db)
    
    if pin_data.old_pin not in pin_dict:
        raise HTTPException(status_code=401, detail="Invalid current PIN")
    
    role = pin_dict[pin_data.old_pin]
    
    # Validate new PIN
    if not pin_data.new_pin.isdigit() or len(pin_data.new_pin) != 4:
        raise HTTPException(status_code=400, detail="New PIN must be exactly 4 digits")
    
    # Check if new PIN is already in use
    if pin_data.new_pin in pin_dict and pin_dict[pin_data.new_pin] != role:
        raise HTTPException(status_code=400, detail="PIN already in use")
    
    # Update PIN
    cursor.execute(
        'UPDATE pins SET pin = ? WHERE role = ?',
        (pin_data.new_pin, role)
    )
    db.commit()
    
    return {"message": "PIN updated successfully"}

@app.post("/add-entry")
async def add_entry(entry: JournalEntry, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    current_time = datetime.utcnow().isoformat()
    cursor.execute(
        'INSERT INTO entries (content, created_at, author) VALUES (?, ?, ?)',
        (entry.content, current_time, entry.author)
    )
    db.commit()
    return {"message": "Entry added successfully", "id": cursor.lastrowid}

@app.get("/entries", response_model=List[JournalEntryResponse])
async def get_entries(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute('SELECT id, content, created_at, author FROM entries ORDER BY created_at DESC')
    entries = cursor.fetchall()
    return [
        JournalEntryResponse(
            id=row[0],
            content=row[1],
            created_at=row[2],
            author=row[3]
        )
        for row in entries
    ]

@app.delete("/entries/{entry_id}")
async def delete_entry(entry_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Entry deleted successfully"}

@app.put("/entries/{entry_id}")
async def update_entry(entry_id: int, entry: JournalEntry, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        'UPDATE entries SET content = ? WHERE id = ?',
        (entry.content, entry_id)
    )
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Entry updated successfully"} 