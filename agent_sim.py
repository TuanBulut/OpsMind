import requests
import time

# Use localhost (Your Windows PC -> Docker mapped port)
API_URL = "http://127.0.0.1:5000"

def run_agent():
    print("🖥️  Server: Production-Server-X is running...")
    print("🔥 ISSUE DETECTED: Disk Full! Reporting to OpsMind HQ...")
    
    payload = {
        "server_name": "Production-Server-X", 
        "error_message": "Error: Disk usage 99%. No space left on device.", 
        "severity": "Critical"
    }
    
    # 1. Create Ticket
    try:
        resp = requests.post(f"{API_URL}/report_incident", json=payload).json()
        ticket_id = resp['ticket_id']
        print(f"🎫 Ticket #{ticket_id} Logged successfully.")
    except Exception as e:
        print(f"❌ Error creating ticket: {e}")
        return

    # 2. Wait for resolution
    print("⏳ Waiting for AI diagnosis and Human Approval...")
    last_status = None
    
    while True:
        try:
            status_data = requests.get(f"{API_URL}/ticket_status/{ticket_id}").json()
            current_status = status_data['status']
            
            # Only print when status changes
            if current_status != last_status:
                if current_status == 'QUEUED':
                    print(f"   [Ticket #{ticket_id}] Status: ⏳ Queued for AI processing...")
                elif current_status == 'PROCESSING':
                    print(f"   [Ticket #{ticket_id}] Status: 🤖 AI is analyzing the issue...")
                elif current_status == 'AWAITING_APPROVAL':
                    print(f"   [Ticket #{ticket_id}] Status: 👤 Waiting for Admin Approval...")
                elif current_status == 'EXECUTED':
                    print(f"\n🚀 APPROVED! Command Received from HQ.")
                    print(f"⌨️  Executing: {status_data.get('ai_fix', 'No fix provided')[:100]}...")
                elif current_status == 'COMPLETED':
                    print(f"✅ Fix Applied. Server returned to normal.")
                    break
                
                last_status = current_status
            
            # Check every second
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            time.sleep(2)
        except KeyError:
            print(f"❌ Ticket #{ticket_id} not found in system")
            break

if __name__ == "__main__":
    run_agent()