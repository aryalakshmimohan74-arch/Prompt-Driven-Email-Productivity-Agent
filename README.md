# Prompt-Driven-Email-Productivity-Agent
# Email Productivity Agent

An intelligent, prompt-driven Email Productivity Agent that automates email management tasks using Claude AI. The system categorizes emails, extracts action items, drafts replies, and provides a chat interface for inbox interaction.

## Features

- **Email Categorization**: Automatically categorizes emails (Important, Newsletter, Spam, To-Do, etc.)
- **Action Item Extraction**: Identifies tasks, deadlines, and priorities from email content
- **Auto-Reply Drafting**: Generates professional email replies based on context
- **Chat Interface**: Ask questions about your emails using natural language
- **Prompt Configuration**: Customize AI behavior through editable prompts
- **Draft Management**: Create, view, and edit email drafts safely
- **Mock Inbox**: Pre-loaded sample emails for testing

##  Architecture

```
Frontend (Streamlit) ←→ Backend API (FastAPI) ←→ API
                              ↓
                         SQLite Database
```

##  Prerequisites

- Python 3.9 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Git

##  Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd email-productivity-agent
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
API_BASE_URL=http://localhost:8000
```

### 5. Create Required Directories

```bash
mkdir -p database
mkdir -p data
```

### 6. Run the Application

#### Option A: Using the Run Script (Recommended)

```bash
chmod +x run.sh
./run.sh
```

#### Option B: Manual Start

**Terminal 1 - Start Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
streamlit run app.py
```

### 7. Access the Application

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

##  Loading Mock Data

1. Click the **"📂 Load Mock"** button in the sidebar
2. This will:
   - Load 20 sample emails
   - Initialize default prompts
   - Process emails with categorization and action items

##  Configuring Prompts

1. Navigate to **" Prompt Configuration"** in the sidebar
2. Edit any of the default prompts:
   - **Categorization**: Controls how emails are categorized
   - **Action Items**: Extracts tasks and deadlines
   - **Auto Reply**: Generates email responses
   - **Summarization**: Creates email summaries
3. Click **"💾 Save"** to apply changes
4. Re-process emails to see the updated behavior

##  Using the Email Chat

1. Go to **" Email Chat"** in the sidebar
2. Select an email or choose "All Emails"
3. Ask questions like:
   - "Summarize this email"
   - "What tasks do I need to do?"
   - "Show me all urgent emails"
   - "Draft a reply declining this meeting"

##  Managing Drafts

1. Navigate to **"Drafts"**
2. View all generated draft emails
3. Click **"Create New Email"** to generate custom emails
4. Edit drafts before copying to your email client
5. **Note**: Drafts are never sent automatically - they're for review only

##  Project Structure

```
email-productivity-agent/
├── backend/
│   ├── app.py                 # FastAPI main application
│   ├── database.py            # SQLite database operations
│   ├── models.py              # Pydantic data models
│   ├── llm_service.py         # Claude API integration
│   ├── email_processor.py     # Email processing logic
│   └── requirements.txt       # Python dependencies
├── frontend/
│   └── app.py                 # Streamlit UI application
├── data/
│   ├── mock_inbox.json        # Sample emails
│   └── default_prompts.json   # Default AI prompts
├── database/
│   └── emails.db              # SQLite database (auto-generated)
├── .env                       # Environment variables (create this)
├── .env.example               # Environment template
├── run.sh                     # Startup script
└── README.md                  # This file
```

##  API Endpoints

### Emails
- `GET /emails` - Get all emails
- `GET /emails/{id}` - Get specific email
- `POST /emails/load-mock` - Load mock inbox
- `POST /emails/process` - Process email batch
- `DELETE /emails` - Delete all emails

### Prompts
- `GET /prompts` - Get all prompts
- `GET /prompts/{name}` - Get specific prompt
- `POST /prompts` - Create/update prompt
- `POST /prompts/load-defaults` - Load default prompts

### Drafts
- `GET /drafts` - Get all drafts
- `GET /drafts/{id}` - Get specific draft
- `POST /drafts` - Create draft
- `DELETE /drafts/{id}` - Delete draft

### Agent
- `POST /agent/chat` - Chat with email agent
- `POST /agent/draft-reply/{id}` - Draft reply to email
- `POST /agent/generate-email` - Generate new email

##  Safety Features

- **No Automatic Sending**: All generated emails are saved as drafts only
- **User Review Required**: Drafts must be manually copied to email client
- **Error Handling**: Graceful handling of API failures
- **Data Privacy**: All data stored locally in SQLite database

## Troubleshooting

### Backend Won't Start
- Check that port 8000 is available
- Verify your ANTHROPIC_API_KEY in .env
- Ensure all dependencies are installed

### Frontend Won't Start
- Check that port 8501 is available
- Verify backend is running
- Check API_BASE_URL in .env

### Emails Not Processing
- Verify your Anthropic API key is valid
- Check backend logs for errors
- Ensure prompts are configured

### Database Issues
- Delete `database/emails.db` and restart
- The database will be recreated automatically

##  Customization

### Adding New Prompt Types

1. Go to Prompt Configuration → "Add New" tab
2. Create a custom prompt (e.g., "priority_detection")
3. Use it in custom processing logic

### Modifying Email Categories

Edit the categorization prompt to include your desired categories:

```
Categories: Important, Newsletter, Spam, To-Do, Financial, Personal, Work
```

### Adding New Email Sources

Modify `backend/email_processor.py` to integrate with:
- Gmail API
- Outlook API
- IMAP servers

##  Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

##  License

This project is for educational purposes. Please ensure you comply with Anthropic's API usage terms.

##  Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation at http://localhost:8000/docs
- Check Anthropic's documentation

## Technical Notes

### LLM Integration
- Uses Claude Sonnet 4 for best performance
- Implements prompt templating system
- Handles JSON extraction from LLM responses

### Database Schema
- **emails**: Stores email data and processing results
- **prompts**: Stores user-configured AI prompts
- **drafts**: Stores generated email drafts

### Error Handling
- Try-catch blocks around all LLM calls
- Graceful degradation on API failures
- User-friendly error messages

---
