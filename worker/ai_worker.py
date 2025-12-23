import time
import mysql.connector
import requests
import os

# Config
DB_HOST = os.getenv("DB_HOST", "mysql")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST, user="root", password="TuanBulut2019", database="IT_Support_Bot"
    )

def ask_ollama(prompt):
    print(f"🔗 Connecting to Ollama at {OLLAMA_HOST}...")
    try:
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # More focused, less creative
                "top_p": 0.9
            }
        }
        r = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=30)
        print("✅ Ollama responded successfully")
        response = r.json()['response'].strip()
        
        # Clean up the response - extract just the command
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            # Skip empty lines, markdown, and explanatory text
            if line and not line.startswith('#') and not line.startswith('```'):
                # If it looks like a command (starts with common commands)
                if any(line.startswith(cmd) for cmd in ['sudo', 'rm', 'df', 'du', 'find', 'apt', 'systemctl', 'docker', 'kill', 'ps']):
                    return line
        
        # If no command found, return first non-empty line
        for line in lines:
            if line.strip():
                return line.strip()
                
        return response[:200]  # Fallback: first 200 chars
        
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to Ollama at {OLLAMA_HOST}")
        return "sudo du -sh /* | sort -rh | head -5"
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        return f"AI Error: {e}"

def process_ticket(ticket):
    print(f"\n🤖 AI Processing Ticket #{ticket['id']}...")
    print(f"   Server: {ticket['server_name']}")
    print(f"   Error: {ticket['error_msg']}")
    
    # 1. Update status to PROCESSING
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE incidents SET status='PROCESSING' WHERE id=%s", (ticket['id'],))
    conn.commit()
    conn.close()
    print("   Status updated to PROCESSING")

    # 2. Ask AI with improved prompt
    prompt = f"""You are a Linux system administrator. A server has this error:

{ticket['error_msg']}

Respond with ONLY a single Linux command to fix this issue. 
Do NOT include explanations, markdown, or multiple commands.
Just output ONE command that would help resolve this issue.

Command:"""
    
    fix_command = ask_ollama(prompt)
    
    print(f"   AI suggested: {fix_command}")

    # 3. Save Fix and wait for Human
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE incidents SET status='AWAITING_APPROVAL', ai_fix=%s WHERE id=%s", (fix_command, ticket['id']))
    conn.commit()
    conn.close()
    print(f"✅ Ticket #{ticket['id']} - AI Fix ready. Waiting for Admin approval.\n")

def main():
    print("=" * 60)
    print("👷 OpsMind Worker Started")
    print("=" * 60)
    print(f"Database: {DB_HOST}")
    print(f"Ollama: {OLLAMA_HOST}")
    print("=" * 60)
    
    print("\n⏳ Waiting for database to be ready...")
    time.sleep(10)
    
    print("✅ Starting ticket processing loop...\n")
    
    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 1. Process new queued tickets
            cursor.execute("SELECT * FROM incidents WHERE status='QUEUED' LIMIT 1")
            ticket = cursor.fetchone()
            
            if ticket:
                conn.close()
                process_ticket(ticket)
                continue
            
            # 2. Mark executed tickets as completed
            cursor.execute("SELECT * FROM incidents WHERE status='EXECUTED' LIMIT 1")
            executed = cursor.fetchone()
            
            if executed:
                cursor.execute("UPDATE incidents SET status='COMPLETED' WHERE id=%s", (executed['id'],))
                conn.commit()
                print(f"✅ Ticket #{executed['id']} marked as COMPLETED\n")
            
            conn.close()
            time.sleep(1)
            
        except mysql.connector.Error as e:
            print(f"❌ Database Error: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Worker Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()