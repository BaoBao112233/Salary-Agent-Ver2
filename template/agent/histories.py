import os
import json
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

class ImageSupportChatHistory(BaseChatMessageHistory):
    """Chat message history that supports images and stores messages in a JSON file."""
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.messages = []
        self._load_messages()
    
    def _load_messages(self):
        """Load messages from the JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    messages_json = json.load(f)
                    
                self.messages = []
                for msg in messages_json:
                    if msg["type"] == "human":
                        # Check if this is a text-only or text+image message
                        if isinstance(msg["data"]["content"], list):
                            # This is a message with image
                            self.messages.append(HumanMessage(content=msg["data"]["content"]))
                        else:
                            # Text-only message
                            self.messages.append(HumanMessage(content=msg["data"]["content"]))
                    elif msg["type"] == "ai":
                        self.messages.append(AIMessage(content=msg["data"]["content"]))
                    elif msg["type"] == "system":
                        self.messages.append(SystemMessage(content=msg["data"]["content"]))
            except (json.JSONDecodeError, FileNotFoundError):
                self.messages = []
        else:
            self.messages = []
    
    def _save_messages(self):
        """Save messages to the JSON file."""
        messages_json = []
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                messages_json.append({
                    "type": "human",
                    "data": {"content": msg.content}
                })
            elif isinstance(msg, AIMessage):
                messages_json.append({
                    "type": "ai",
                    "data": {"content": msg.content}
                })
            elif isinstance(msg, SystemMessage):
                messages_json.append({
                    "type": "system",
                    "data": {"content": msg.content}
                })
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        with open(self.file_path, "w") as f:
            json.dump(messages_json, f, indent=2)
    
    def add_message(self, message):
        """Add a message to the store."""
        self.messages.append(message)
        # print(self.messages)
        self._save_messages()

    
    def add_user_message(self, message, image_url=None):
        """Add a user message, optionally with an image."""
        if image_url:
            # Create a message with both text and image
            content = [
                {"type": "text", "text": message},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]

            self.add_message(HumanMessage(content=content))    
            
        else:

            # Text-only message
            self.add_message(HumanMessage(content=message))
            

    
    def add_ai_message(self, message):
        """Add an AI message."""
        self.add_message(AIMessage(content=message))
        print(self.messages)
    
    def clear(self):
        """Clear all messages."""
        self.messages = []
        self._save_messages()
