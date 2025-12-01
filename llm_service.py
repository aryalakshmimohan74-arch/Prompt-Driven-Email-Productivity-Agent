import os
from dotenv import load_dotenv
from anthropic import Anthropic
from typing import Dict, Any, List

load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        # Simple initialization - NO proxies or custom http_client
        self.client = Anthropic(api_key=api_key)
    
    def classify_email(self, email_content: str) -> Dict[str, Any]:
        """Classify email into categories and extract action items"""
        prompt = f"""
        Analyze this email and respond in JSON format only:
        {{
            "category": "one of: work, personal, marketing, urgent, newsletter, trash",
            "action_items": ["list", "of", "actionable", "tasks", "or", "[]"]
        }}
        
        Email: {email_content[:2000]}  # Truncate for token limits
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            content = response.content[0].text.strip()
            
            # Simple JSON extraction (improve with json.loads in production)
            if "{" in content and "}" in content:
                return {"raw": content, "parsed": eval(content)}  # Use json.loads in prod
            else:
                return {"category": "uncategorized", "action_items": []}
                
        except Exception as e:
            return {"category": "error", "action_items": [], "error": str(e)}
    
    def generate_reply(self, email_content: str, context: str = "") -> str:
        """Generate professional email reply"""
        prompt = f"""
        Write a professional, concise reply to this email. Keep it under 150 words.
        
        Original email: {email_content[:1500]}
        Context: {context}
        
        Reply:
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"Sorry, could not generate reply: {str(e)}"
