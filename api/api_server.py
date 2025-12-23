from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import os

app = FastAPI()

# Config
DB_HOST = os.getenv("DB_HOST", "mysql")
DB_USER = "root"
DB_PASS = "TuanBulut2019"
DB_NAME = "IT_Support_Bot"

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
    )

class Incident(BaseModel):
    server_name: str
    error_message: str
    severity: str

# 1. Report Incident (Called by Agent)
@app.post("/report_incident")
def report_incident(data: Incident):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    sql = "INSERT INTO incidents (server_name, error_msg, severity, status) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (data.server_name, data.error_message, data.severity, 'QUEUED'))
    conn.commit()
    
    ticket_id = cursor.lastrowid
    conn.close()
    return {"status": "reported", "ticket_id": ticket_id}

# 2. Check Status (Called by Agent)
@app.get("/ticket_status/{ticket_id}")
def get_status(ticket_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status, ai_fix FROM incidents WHERE id=%s", (ticket_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result
    raise HTTPException(status_code=404, detail="Ticket not found")

# 3. Approve Fix (Called by Dashboard) - NOW MARKS AS EXECUTED
@app.post("/approve_fix/{ticket_id}")
def approve_fix(ticket_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Change status to EXECUTED (removes from dashboard immediately)
    sql = "UPDATE incidents SET status='EXECUTED' WHERE id=%s AND status='AWAITING_APPROVAL'"
    cursor.execute(sql, (ticket_id,))
    conn.commit()
    
    rows = cursor.rowcount
    conn.close()
    
    if rows == 0:
        raise HTTPException(status_code=404, detail="Ticket not found or already processed")
        
    return {"message": "Fix approved and executed"}
# 4. Reset Tickets (For Testing)
@app.delete("/reset_tickets")
def reset_tickets():
    """Delete all completed/executed tickets - for testing only"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM incidents WHERE status IN ('EXECUTED', 'COMPLETED')")
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    
    return {"message": f"Deleted {deleted} old tickets"}