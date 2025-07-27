#!/usr/bin/env python3
# File: SimpleStandalone.py  
# Super simple version for testing Windows packaging
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sqlite3
import shutil
from pathlib import Path

app = FastAPI(title="AndyLibrary Simple Test")

@app.get("/")
async def root():
    return {"message": "🎉 AndyLibrary Standalone Working!", "books": get_book_count()}

@app.get("/api/health")  
async def health():
    return {"status": "healthy", "books": get_book_count()}

def get_book_count():
    try:
        db_path = Path("Data/MyLibrary.db")
        if not db_path.exists():
            # Try to copy from main installation
            source = Path("../Data/Databases/MyLibrary.db")
            if source.exists():
                Path("Data").mkdir(exist_ok=True)
                shutil.copy2(source, db_path)
        
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            conn.close()
            return count
    except:
        pass
    return 0

if __name__ == "__main__":
    print("🚀 Simple AndyLibrary Standalone Test")
    print("📚 Database books:", get_book_count())
    print("🌐 Starting server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)