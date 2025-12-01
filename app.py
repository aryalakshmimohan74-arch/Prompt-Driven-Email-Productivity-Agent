import streamlit as st
import requests
import json
from datetime import datetime
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Email Productivity Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .email-card {
        background-color: #f8f9fa;
        border-left: 4px solid #4CAF50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .category-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 5px;
    }
    .important { background-color: #ff5252; color: white; }
    .todo { background-color: #ffc107; color: black; }
    .newsletter { background-color: #2196f3; color: white; }
    .spam { background-color: #9e9e9e; color: white; }
    .social { background-color: #4caf50; color: white; }
    .notification { background-color: #00bcd4; color: white; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'emails' not in st.session_state:
    st.session_state.emails = []
if 'prompts' not in st.session_state:
    st.session_state.prompts = {}
if 'selected_email' not in st.session_state:
    st.session_state.selected_email = None
if 'drafts' not in st.session_state:
    st.session_state.drafts = []

# Helper functions
def load_emails():
    """Fetch all emails from backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/emails")
        if response.status_code == 200:
            st.session_state.emails = response.json()
            return True
        return False
    except Exception as e:
        st.error(f"Error loading emails: {str(e)}")
        return False

def load_prompts():
    """Fetch all prompts from backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/prompts")
        if response.status_code == 200:
            prompts = response.json()
            st.session_state.prompts = {p['name']: p for p in prompts}
            return True
        return False
    except Exception as e:
        st.error(f"Error loading prompts: {str(e)}")
        return False

def load_drafts():
    """Fetch all drafts from backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/drafts")
        if response.status_code == 200:
            st.session_state.drafts = response.json()
            return True
        return False
    except Exception as e:
        st.error(f"Error loading drafts: {str(e)}")
        return False

def load_mock_inbox():
    """Load mock inbox data"""
    try:
        with open('data/mock_inbox.json', 'r') as f:
            mock_data = json.load(f)
        response = requests.post(f"{API_BASE_URL}/emails/load-mock", json=mock_data)
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        st.error(f"Error loading mock inbox: {str(e)}")
        return False

def load_default_prompts():
    """Load default prompts"""
    try:
        with open('data/default_prompts.json', 'r') as f:
            default_prompts = json.load(f)
        response = requests.post(f"{API_BASE_URL}/prompts/load-defaults", json=default_prompts)
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        st.error(f"Error loading default prompts: {str(e)}")
        return False

def get_category_class(category):
    """Get CSS class for category"""
    if category:
        return category.lower().replace(" ", "")
    return "notification"

# Sidebar
with st.sidebar:
    st.title("📧 Email Agent")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["📥 Inbox", "🧠 Prompt Configuration", "💬 Email Chat", "✉️ Drafts"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick Actions
    st.subheader("Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            load_emails()
            load_prompts()
            load_drafts()
            st.success("Refreshed!")
    
    with col2:
        if st.button("📂 Load Mock", use_container_width=True):
            with st.spinner("Loading mock inbox..."):
                if load_default_prompts() and load_mock_inbox():
                    load_emails()
                    load_prompts()
                    st.success("Mock inbox loaded!")
                else:
                    st.error("Failed to load mock data")
    
    if st.button("🗑️ Clear All Emails", use_container_width=True):
        if st.confirm("Are you sure? This will delete all emails!"):
            response = requests.delete(f"{API_BASE_URL}/emails")
            if response.status_code == 200:
                st.session_state.emails = []
                st.success("All emails cleared!")
    
    st.markdown("---")
    st.caption(f"Total Emails: {len(st.session_state.emails)}")
    st.caption(f"Total Drafts: {len(st.session_state.drafts)}")

# Main content area
if page == "📥 Inbox":
    st.title("📥 Email Inbox")
    
    # Load emails if not already loaded
    if not st.session_state.emails:
        load_emails()
    
    # Filter options
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search_term = st.text_input("🔍 Search emails", placeholder="Search by subject or sender...")
    with col2:
        categories = ["All"] + list(set([e.get('category', 'Uncategorized') for e in st.session_state.emails]))
        selected_category = st.selectbox("Filter by category", categories)
    with col3:
        st.write("")
        st.write("")
        if st.button("↻ Refresh Inbox"):
            load_emails()
    
    # Filter emails
    filtered_emails = st.session_state.emails
    if search_term:
        filtered_emails = [e for e in filtered_emails if 
                          search_term.lower() in e['subject'].lower() or 
                          search_term.lower() in e['sender'].lower()]
    if selected_category != "All":
        filtered_emails = [e for e in filtered_emails if e.get('category') == selected_category]
    
    st.markdown(f"**Showing {len(filtered_emails)} emails**")
    st.markdown("---")
    
    # Display emails
    for email in filtered_emails:
        category = email.get('category', 'Uncategorized')
        category_class = get_category_class(category)
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="email-card">
                    <span class="category-badge {category_class}">{category}</span>
                    <h4 style="margin: 5px 0;">{email['subject']}</h4>
                    <p style="margin: 5px 0; color: #666;">
                        <strong>From:</strong> {email['sender']} | 
                        <strong>Date:</strong> {email['timestamp']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("View Details", key=f"view_{email['id']}"):
                    st.session_state.selected_email = email['id']
                    st.rerun()
        
        # Show details if selected
        if st.session_state.selected_email == email['id']:
            with st.expander("📧 Email Details", expanded=True):
                st.markdown(f"**Subject:** {email['subject']}")
                st.markdown(f"**From:** {email['sender']}")
                st.markdown(f"**Date:** {email['timestamp']}")
                st.markdown("**Body:**")
                st.text_area("Email body", email['body'], height=200, key=f"body_{email['id']}", disabled=True)
                
                # Action items
                if email.get('action_items'):
                    st.markdown("**📋 Action Items:**")
                    try:
                        action_data = json.loads(email['action_items'])
                        if action_data.get('has_action_items') and action_data.get('items'):
                            for item in action_data['items']:
                                priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                                priority_icon = priority_color.get(item.get('priority', 'medium'), "⚪")
                                st.markdown(f"{priority_icon} **{item['task']}**")
                                if item.get('deadline'):
                                    st.caption(f"Deadline: {item['deadline']}")
                        else:
                            st.info("No action items found")
                    except:
                        st.text(email['action_items'])
                
                # Actions
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("💬 Chat about this email", key=f"chat_{email['id']}"):
                        st.session_state.selected_email = email['id']
                        st.session_state.page = "💬 Email Chat"
                with col2:
                    if st.button("✉️ Draft Reply", key=f"reply_{email['id']}"):
                        with st.spinner("Drafting reply..."):
                            response = requests.post(f"{API_BASE_URL}/agent/draft-reply/{email['id']}")
                            if response.status_code == 200:
                                st.success("Draft created! Check the Drafts tab.")
                                load_drafts()
                with col3:
                    if st.button("✖️ Close", key=f"close_{email['id']}"):
                        st.session_state.selected_email = None
                        st.rerun()

elif page == "🧠 Prompt Configuration":
    st.title("🧠 Prompt Configuration")
    st.markdown("Configure the AI prompts that control email processing behavior.")
    
    # Load prompts if not already loaded
    if not st.session_state.prompts:
        load_prompts()
    
    # Tabs for different prompts
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📂 Categorization", 
        "📋 Action Items", 
        "✉️ Auto Reply", 
        "📝 Summary",
        "➕ Add New"
    ])
    
    prompt_names = {
        "categorization": "📂 Categorization",
        "action_items": "📋 Action Items",
        "auto_reply": "✉️ Auto Reply",
        "summarization": "📝 Summary"
    }
    
    tabs = [tab1, tab2, tab3, tab4]
    prompt_keys = ["categorization", "action_items", "auto_reply", "summarization"]
    
    for tab, prompt_key in zip(tabs, prompt_keys):
        with tab:
            prompt_data = st.session_state.prompts.get(prompt_key, {})
            
            st.subheader(f"Edit {prompt_names[prompt_key]} Prompt")
            
            description = st.text_input(
                "Description",
                value=prompt_data.get('description', ''),
                key=f"desc_{prompt_key}"
            )
            
            content = st.text_area(
                "Prompt Content",
                value=prompt_data.get('content', ''),
                height=300,
                key=f"content_{prompt_key}",
                help="This prompt will be used by the AI to process emails"
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("💾 Save", key=f"save_{prompt_key}"):
                    data = {
                        "name": prompt_key,
                        "content": content,
                        "description": description
                    }
                    response = requests.post(f"{API_BASE_URL}/prompts", json=data)
                    if response.status_code == 200:
                        st.success("Prompt saved successfully!")
                        load_prompts()
            
            with col2:
                st.caption("Remember to save your changes!")
    
    # Add new prompt tab
    with tab5:
        st.subheader("➕ Add New Custom Prompt")
        
        new_name = st.text_input("Prompt Name", placeholder="e.g., priority_detection")
        new_description = st.text_input("Description", placeholder="What does this prompt do?")
        new_content = st.text_area("Prompt Content", height=300, placeholder="Enter your prompt here...")
        
        if st.button("Create Prompt"):
            if new_name and new_content:
                data = {
                    "name": new_name,
                    "content": new_content,
                    "description": new_description
                }
                response = requests.post(f"{API_BASE_URL}/prompts", json=data)
                if response.status_code == 200:
                    st.success(f"Prompt '{new_name}' created successfully!")
                    load_prompts()
            else:
                st.error("Please provide both name and content")

elif page == "💬 Email Chat":
    st.title("💬 Email Agent Chat")
    st.markdown("Ask questions about your emails or get help managing your inbox.")
    
    # Email selection
    if st.session_state.emails:
        email_options = ["All Emails"] + [f"[{e['id']}] {e['subject']}" for e in st.session_state.emails]
        selected_option = st.selectbox("Select Email Context", email_options)
        
        if selected_option != "All Emails":
            email_id = int(selected_option.split("]")[0][1:])
            st.session_state.selected_email = email_id
        else:
            st.session_state.selected_email = None
    
    st.markdown("---")
    
    # Chat interface
    user_query = st.text_area(
        "Your Question",
        placeholder="E.g., 'Summarize this email', 'What tasks do I need to do?', 'Show me urgent emails'",
        height=100
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🚀 Ask", use_container_width=True):
            if user_query:
                with st.spinner("Thinking..."):
                    data = {
                        "query": user_query,
                        "email_id": st.session_state.selected_email
                    }
                    response = requests.post(f"{API_BASE_URL}/agent/chat", json=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.markdown("### 🤖 Agent Response")
                        st.info(result['response'])
                    else:
                        st.error("Failed to get response")
            else:
                st.warning("Please enter a question")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Summarize All", use_container_width=True):
            with st.spinner("Analyzing..."):
                data = {"query": "Give me a summary of all emails in my inbox, organized by category"}
                response = requests.post(f"{API_BASE_URL}/agent/chat", json=data)
                if response.status_code == 200:
                    st.success("Summary generated!")
                    st.info(response.json()['response'])
    
    with col2:
        if st.button("⚠️ Show Urgent", use_container_width=True):
            with st.spinner("Finding urgent emails..."):
                data = {"query": "Which emails are urgent and require immediate attention?"}
                response = requests.post(f"{API_BASE_URL}/agent/chat", json=data)
                if response.status_code == 200:
                    st.success("Urgent emails found!")
                    st.warning(response.json()['response'])
    
    with col3:
        if st.button("📋 List Tasks", use_container_width=True):
            with st.spinner("Extracting tasks..."):
                data = {"query": "List all the tasks and action items from my emails"}
                response = requests.post(f"{API_BASE_URL}/agent/chat", json=data)
                if response.status_code == 200:
                    st.success("Tasks listed!")
                    st.info(response.json()['response'])

elif page == "✉️ Drafts":
    st.title("✉️ Email Drafts")
    st.markdown("View, edit, and manage your email drafts.")
    
    # Load drafts if not already loaded
    if not st.session_state.drafts:
        load_drafts()
    
    # Create new draft section
    with st.expander("➕ Create New Email", expanded=False):
        instruction = st.text_area(
            "Describe the email you want to create",
            placeholder="E.g., 'Write a professional email declining a meeting request politely'",
            height=100
        )
        
        context = st.text_input(
            "Additional Context (optional)",
            placeholder="Any specific details to include..."
        )
        
        if st.button("Generate Email"):
            if instruction:
                with st.spinner("Generating email..."):
                    response = requests.post(
                        f"{API_BASE_URL}/agent/generate-email",
                        params={"instruction": instruction, "context": context}
                    )
                    if response.status_code == 200:
                        st.success("Email draft created!")
                        load_drafts()
                        st.rerun()
            else:
                st.warning("Please provide instructions")
    
    st.markdown("---")
    
    # Display drafts
    if st.session_state.drafts:
        st.markdown(f"**{len(st.session_state.drafts)} draft(s)**")
        
        for draft in st.session_state.drafts:
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"### {draft['subject']}")
                    st.caption(f"Created: {draft['created_at']}")
                
                with col2:
                    if st.button("🗑️", key=f"delete_draft_{draft['id']}"):
                        response = requests.delete(f"{API_BASE_URL}/drafts/{draft['id']}")
                        if response.status_code == 200:
                            st.success("Draft deleted!")
                            load_drafts()
                            st.rerun()
                
                with st.expander("View/Edit Draft"):
                    edited_subject = st.text_input(
                        "Subject",
                        value=draft['subject'],
                        key=f"subject_{draft['id']}"
                    )
                    
                    edited_body = st.text_area(
                        "Body",
                        value=draft['body'],
                        height=300,
                        key=f"draft_body_{draft['id']}"
                    )
                    
                    st.info("💡 Note: This is a DRAFT. It will not be sent automatically.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.button("📋 Copy to Clipboard", key=f"copy_{draft['id']}")
                    with col2:
                        st.caption("Copy this draft to your email client to send")
                
                st.markdown("---")
    else:
        st.info("No drafts yet. Create one using the Email Chat or by replying to emails!")

# Footer
st.markdown("---")
st.caption("Email Productivity Agent | Powered by Claude AI")
