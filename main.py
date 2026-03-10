import os
import json
import asyncio
import time
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import anthropic

app = FastAPI(title="Mister Mac AI Copilot")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "demo-key"))

# Load mock data
def load_json(filename):
    try:
        with open(f"data/{filename}", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

customers_data = load_json("customers.json")
conversations_data = load_json("conversations.json")
apple_knowledge = load_json("apple_knowledge.json")
appointments_data = load_json("appointments.json")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start-session")
async def start_session(customer_id: str = Form(...)):
    """Start a new copilot session for a customer"""
    customer = customers_data.get(customer_id, {})
    appointment = appointments_data.get(customer_id, {})
    
    return {
        "session_id": f"session_{customer_id}_{int(time.time())}",
        "customer": customer,
        "appointment": appointment,
        "status": "ready"
    }

@app.get("/stream-analysis/{session_id}")
async def stream_analysis(session_id: str):
    """Stream real-time AI analysis and guidance"""
    
    async def generate_analysis():
        # Simulate receiving customer screen and conversation
        scenarios = [
            {
                "timestamp": "00:15",
                "screen": "iPhone home screen visible",
                "conversation": "Customer: My email isn't working, I can't see any new messages",
                "analysis": "Customer reporting email sync issue",
                "guidance": "Ask customer to open Mail app and check last update time"
            },
            {
                "timestamp": "00:32", 
                "screen": "Mail app open, showing 'Cannot Get Mail' error",
                "conversation": "Customer: It says 'Cannot Get Mail' and there's a red exclamation mark",
                "analysis": "Mail app showing connection error - likely server settings issue",
                "guidance": "Guide customer to Settings > Mail > Accounts. Check if account shows error indicator"
            },
            {
                "timestamp": "00:58",
                "screen": "Settings > Mail > Accounts visible, Gmail account with error badge",
                "conversation": "Customer: Yes, I see my Gmail has a little warning triangle",
                "analysis": "Gmail account authentication expired - common after iOS update",
                "guidance": "Tap on Gmail account, then 'Re-enter Password'. This will refresh authentication tokens"
            },
            {
                "timestamp": "01:24",
                "screen": "Password entry dialog for Gmail account",
                "conversation": "Customer: OK I'm entering my password now",
                "analysis": "Customer following password re-entry steps correctly",
                "guidance": "After password entry, watch for 'Verifying...' then 'Account verified' confirmation"
            },
            {
                "timestamp": "01:45",
                "screen": "Account verified, returning to Mail app",
                "conversation": "Customer: It says verified! Going back to Mail now",
                "analysis": "Authentication successful, Mail should sync within 30 seconds",
                "guidance": "Pull down in Mail app to force refresh. New emails should appear within 30 seconds"
            },
            {
                "timestamp": "02:10",
                "screen": "Mail app showing 'Updating...' with new emails loading",
                "conversation": "Customer: Oh wow, emails are coming in now! Thank you so much!",
                "analysis": "Issue resolved successfully - authentication fix worked",
                "guidance": "Problem solved! You can let customer know to restart iPhone if they see this issue again"
            }
        ]
        
        for scenario in scenarios:
            # Simulate processing delay
            await asyncio.sleep(3)
            
            # Generate AI guidance using Claude API (fallback to mock if no key)
            if os.environ.get("ANTHROPIC_API_KEY") and os.environ.get("ANTHROPIC_API_KEY") != "demo-key":
                try:
                    message = client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=300,
                        system="""You are an AI copilot helping a junior technician provide Apple technical support. 
                        Based on the customer's screen and conversation, provide specific step-by-step guidance that the technician can read directly to the customer.
                        Be conversational but precise. Focus on the immediate next step.""",
                        messages=[{
                            "role": "user", 
                            "content": f"Screen: {scenario['screen']}\nCustomer said: {scenario['conversation']}\n\nWhat should the technician tell the customer to do next?"
                        }]
                    )
                    ai_guidance = message.content[0].text
                except:
                    ai_guidance = scenario['guidance']  # Fallback to mock
            else:
                ai_guidance = scenario['guidance']
            
            data = {
                "timestamp": scenario['timestamp'],
                "screen_description": scenario['screen'],
                "conversation_snippet": scenario['conversation'],
                "ai_analysis": scenario['analysis'],
                "suggested_guidance": ai_guidance,
                "confidence": 0.92
            }
            
            yield f"data: {json.dumps(data)}\n\n"
        
        # Final completion message
        await asyncio.sleep(2)
        yield f"data: {json.dumps({'status': 'completed', 'message': 'Session completed successfully'})}\n\n"

    return StreamingResponse(generate_analysis(), media_type="text/plain")

@app.get("/knowledge-search")
async def knowledge_search(query: str = ""):
    """Search Apple knowledge base for relevant troubleshooting steps"""
    if not query:
        return {"results": []}
    
    # Mock knowledge base search
    relevant_articles = [
        {
            "title": "iPhone Mail App Cannot Get Mail Error",
            "summary": "Common authentication and server setting issues",
            "steps": [
                "Check account settings in Settings > Mail > Accounts",
                "Re-enter password for affected account",
                "Toggle Mail sync off/on if password correct",
                "Delete and re-add account as last resort"
            ]
        },
        {
            "title": "Email Sync Issues After iOS Update", 
            "summary": "iOS updates often require re-authentication",
            "steps": [
                "Go to Settings > Mail > Accounts",
                "Look for accounts with warning triangles",
                "Tap account and select 'Re-enter Password'",
                "Wait for verification, then test Mail app"
            ]
        }
    ]
    
    return {"results": relevant_articles}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)