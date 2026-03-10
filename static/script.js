let currentSession = null;
let sessionTimer = null;
let sessionStartTime = null;
let eventSource = null;

// Customer data for demo
const customerData = {
    customer_1: {
        name: "Sarah Johnson",
        appointment_type: "iPhone Email Setup",
        appointment_time: "Today 2:30 PM",
        history: "Previous visits: New iPhone setup (Nov 2023), iCloud backup issue (Dec 2023)",
        screen_images: ["broken-email-1.png", "broken-email-2.png"]
    },
    customer_2: {
        name: "Mike Chen", 
        appointment_type: "Security Concern",
        appointment_time: "Today 3:00 PM",
        history: "Regular customer since 2020. Uses iPhone 14 Pro for business.",
        screen_images: ["spam-warning.png"]
    },
    customer_3: {
        name: "Linda Rodriguez",
        appointment_type: "iCloud Sync Issues", 
        appointment_time: "Today 3:30 PM",
        history: "Previous visits: iPhone 12 upgrade (Jan 2024), Apple Watch setup (Feb 2024)",
        screen_images: ["broken-email-1.png"]
    }
};

document.addEventListener('DOMContentLoaded', function() {
    const customerSelect = document.getElementById('customer-select');
    const startButton = document.getElementById('start-session');
    const dashboard = document.getElementById('dashboard');
    const customerSelection = document.getElementById('customer-selection');

    // Enable start button when customer is selected
    customerSelect.addEventListener('change', function() {
        startButton.disabled = !this.value;
    });

    // Start copilot session
    startButton.addEventListener('click', async function() {
        const selectedCustomer = customerSelect.value;
        if (!selectedCustomer) return;

        try {
            startButton.disabled = true;
            startButton.textContent = 'Starting...';

            // Start session
            const response = await fetch('/start-session', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `customer_id=${selectedCustomer}`
            });
            
            const sessionData = await response.json();
            currentSession = sessionData.session_id;

            // Update UI with customer info
            updateCustomerInfo(selectedCustomer);
            
            // Show dashboard, hide selection
            customerSelection.style.display = 'none';
            dashboard.style.display = 'block';

            // Start session timer
            startSessionTimer();

            // Start AI analysis stream
            startAnalysisStream();

        } catch (error) {
            console.error('Error starting session:', error);
            startButton.disabled = false;
            startButton.textContent = 'Start AI Copilot';
        }
    });
});

function updateCustomerInfo(customerId) {
    const customer = customerData[customerId];
    if (!customer) return;

    document.getElementById('customer-name').textContent = customer.name;
    document.getElementById('appointment-type').textContent = customer.appointment_type;
    document.getElementById('appointment-time').textContent = customer.appointment_time;
    document.getElementById('customer-history').textContent = customer.history;
    document.getElementById('session-status').textContent = 'Active';
    document.getElementById('session-status').className = 'badge badge-green';
}

function startSessionTimer() {
    sessionStartTime = Date.now();
    sessionTimer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        document.getElementById('session-timer').textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

function startAnalysisStream() {
    if (eventSource) {
        eventSource.close();
    }

    eventSource = new EventSource(`/stream-analysis/${currentSession}`);
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.status === 'completed') {
            eventSource.close();
            document.getElementById('session-status').textContent = 'Completed';
            document.getElementById('session-status').className = 'badge badge-gray';
            return;
        }

        // Update screen viewer
        updateScreenViewer(data.screen_description);
        
        // Add conversation item
        addConversationItem(data.timestamp, data.conversation_snippet);
        
        // Add AI guidance
        addGuidanceItem(data.timestamp, data.suggested_guidance, data.ai_analysis, data.confidence);
    };

    eventSource.onerror = function(event) {
        console.error('EventSource error:', event);
        eventSource.close();
    };
}

function updateScreenViewer(screenDescription) {
    const screenViewer = document.getElementById('screen-viewer');
    const analysisOverlay = document.getElementById('screen-analysis');
    
    // For demo, show description instead of actual screen
    screenViewer.innerHTML = `
        <div style="padding: 24px; text-align: center;">
            <div style="font-size: 16px; font-weight: 600; color: #141413; margin-bottom: 12px;">
                📱 Customer Screen
            </div>
            <div style="font-size: 14px; color: #4a4845; background: rgba(255,255,255,0.8); padding: 16px; border-radius: 8px;">
                ${screenDescription}
            </div>
        </div>
    `;
    
    // Show analysis overlay
    analysisOverlay.style.display = 'block';
    analysisOverlay.textContent = '🔍 AI Analyzing...';
}

function addConversationItem(timestamp, conversation) {
    const conversationFeed = document.getElementById('conversation-feed');
    
    // Clear empty state on first item
    if (conversationFeed.querySelector('.empty-state')) {
        conversationFeed.innerHTML = '';
    }

    const item = document.createElement('div');
    item.className = 'conversation-item';
    item.innerHTML = `
        <div class="conversation-timestamp">${timestamp}</div>
        <div>${conversation}</div>
    `;
    
    conversationFeed.appendChild(item);
    conversationFeed.scrollTop = conversationFeed.scrollHeight;
}

function addGuidanceItem(timestamp, guidance, analysis, confidence) {
    const guidancePanel = document.getElementById('guidance-panel');
    
    // Clear empty state on first item
    if (guidancePanel.querySelector('.empty-state')) {
        guidancePanel.innerHTML = '';
    }

    const item = document.createElement('div');
    item.className = 'guidance-item';
    item.innerHTML = `
        <div class="guidance-confidence">AI CONFIDENCE: ${Math.round(confidence * 100)}% • ${timestamp}</div>
        <div class="guidance-text">${guidance}</div>
        <div class="guidance-analysis">Analysis: ${analysis}</div>
    `;
    
    guidancePanel.appendChild(item);
    guidancePanel.scrollTop = guidancePanel.scrollHeight;
}