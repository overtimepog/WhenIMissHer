from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, UTC
import aiosqlite
from typing import List, AsyncGenerator
import os
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="When I Miss Her API", lifespan=lifespan)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = 'journal.db'

# Database initialization
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    async with aiosqlite.connect(DATABASE_URL) as db:
        yield db

# Initialize database and tables
async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            author TEXT NOT NULL
        )''')
        
        await db.execute('''
        CREATE TABLE IF NOT EXISTS pins (
            role TEXT PRIMARY KEY,
            pin TEXT NOT NULL
        )''')
        
        await db.execute('''
        CREATE TABLE IF NOT EXISTS labels (
            role TEXT PRIMARY KEY,
            label TEXT NOT NULL
        )''')
        
        # Insert default pins if not exist
        await db.execute('INSERT OR IGNORE INTO pins (role, pin) VALUES (?, ?)', ('you', '6278'))
        await db.execute('INSERT OR IGNORE INTO pins (role, pin) VALUES (?, ?)', ('her', '1234'))

        # Insert default labels if not exist
        await db.execute('INSERT OR IGNORE INTO labels (role, label) VALUES (?, ?)', ('you', 'You'))
        await db.execute('INSERT OR IGNORE INTO labels (role, label) VALUES (?, ?)', ('her', 'Her'))

        #set this to new years 2025 
        await db.execute('INSERT OR IGNORE INTO entries (content, created_at, author) VALUES (?, ?, ?)', 
            ('I wish I was kissing you right now', '2025-01-01T00:00:00Z', 'you'))
        await db.commit()

# Models
class PinInput(BaseModel):
    pin: str

class PinChange(BaseModel):
    old_pin: str
    new_pin: str

class LabelChange(BaseModel):
    pin: str
    new_label: str

class JournalEntry(BaseModel):
    content: str
    author: str = "you"

class JournalEntryResponse(BaseModel):
    id: int
    content: str
    created_at: str
    author: str

class LabelsResponse(BaseModel):
    you: str
    her: str

async def get_pin_data(db: aiosqlite.Connection):
    async with db.execute('SELECT role, pin FROM pins') as cursor:
        rows = await cursor.fetchall()
        return {pin: role for role, pin in rows}

@app.get("/labels")
async def get_labels(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute('SELECT role, label FROM labels') as cursor:
        rows = await cursor.fetchall()
        labels = dict(rows)
        return LabelsResponse(you=labels['you'], her=labels['her'])

@app.post("/change-label")
async def change_label(label_data: LabelChange, db: aiosqlite.Connection = Depends(get_db)):
    pin_dict = await get_pin_data(db)
    
    if label_data.pin not in pin_dict:
        raise HTTPException(status_code=401, detail="Invalid PIN")
    
    role = pin_dict[label_data.pin]
    
    # Validate label
    if not label_data.new_label or len(label_data.new_label) > 20:
        raise HTTPException(status_code=400, detail="Label must be between 1 and 20 characters")
    
    # Update label
    await db.execute(
        'UPDATE labels SET label = ? WHERE role = ?',
        (label_data.new_label, role)
    )
    await db.commit()
    
    return {"message": "Label updated successfully"}

@app.post("/verify-pin")
async def verify_pin(pin_data: PinInput, db: aiosqlite.Connection = Depends(get_db)):
    pin = pin_data.pin
    pin_dict = await get_pin_data(db)
    if pin in pin_dict:
        return {"role": pin_dict[pin]}
    raise HTTPException(status_code=401, detail="Invalid PIN")

@app.post("/change-pin")
async def change_pin(pin_data: PinChange, db: aiosqlite.Connection = Depends(get_db)):
    pin_dict = await get_pin_data(db)
    
    if pin_data.old_pin not in pin_dict:
        raise HTTPException(status_code=401, detail="Invalid current PIN")
    
    role = pin_dict[pin_data.old_pin]
    
    # Validate new PIN
    if not pin_data.new_pin.isdigit() or len(pin_data.new_pin) != 4:
        raise HTTPException(status_code=400, detail="New PIN must be exactly 4 digits")
    
    # Update PIN
    await db.execute(
        'UPDATE pins SET pin = ? WHERE role = ?',
        (pin_data.new_pin, role)
    )
    await db.commit()
    
    return {"message": "PIN updated successfully"}

@app.post("/add-entry")
async def add_entry(entry: JournalEntry, db: aiosqlite.Connection = Depends(get_db)):
    current_time = datetime.now(UTC).isoformat()
    
    await db.execute(
        'INSERT INTO entries (content, created_at, author) VALUES (?, ?, ?)',
        (entry.content, current_time, entry.author)
    )
    await db.commit()
    
    async with db.execute('SELECT last_insert_rowid()') as cursor:
        entry_id = await cursor.fetchone()
        return {"id": entry_id[0], "content": entry.content, "created_at": current_time, "author": entry.author}

@app.get("/entries", response_model=List[JournalEntryResponse])
async def get_entries(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute('SELECT id, content, created_at, author FROM entries ORDER BY created_at DESC') as cursor:
        entries = await cursor.fetchall()
        return [
            JournalEntryResponse(
                id=entry[0],
                content=entry[1],
                created_at=entry[2],
                author=entry[3]
            )
            for entry in entries
        ]

@app.delete("/entries/{entry_id}")
async def delete_entry(entry_id: int, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
    await db.commit()
    return {"message": "Entry deleted successfully"}

@app.put("/entries/{entry_id}")
async def update_entry(entry_id: int, entry: JournalEntry, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute(
        'UPDATE entries SET content = ?, author = ? WHERE id = ?',
        (entry.content, entry.author, entry_id)
    )
    await db.commit()
    return {"message": "Entry updated successfully"} 