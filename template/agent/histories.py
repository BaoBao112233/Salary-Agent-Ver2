import os
import json
import redis
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from template.configs.environments import env


class RedisSupportChatHistory(BaseChatMessageHistory):
    """Unified chat history supporting text+image, with Redis or File storage backend."""

    def __init__(self, session_id: str, user_id: str, storage: str = "redis", ttl: int = 3600):
        """
        Initialize chat history with flexible storage backend.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            storage: Storage backend - "redis" or "file" (default: "redis")
            ttl: Time-to-live for Redis cache in seconds (default: 3600)
        """
        super().__init__()
        self.session_id = str(session_id)
        self.user_id = str(user_id)
        self.storage = storage
        self.ttl = ttl
        self.messages = []
        
        # Initialize storage backend
        if self.storage == "redis":
            try:
                self.redis_client = redis.Redis(
                    host=env.REDIS_HOST,
                    port=env.REDIS_PORT,
                    db=env.REDIS_DB,
                    decode_responses=True,
                )
                # Test connection
                self.redis_client.ping()
            except Exception as e:
                print(f"Redis connection failed: {e}. Falling back to file storage.")
                self.storage = "file"
        
        if self.storage == "file":
            # Setup file path for file-based storage
            self.file_path = f"memories/chat_history_{self.session_id}_{self.user_id}.json"
            
        self._load_messages()

    # -------------------------------
    # Core storage methods
    # -------------------------------
    def _get_redis_key(self):
        """Get Redis key for chat history."""
        return f"chat_history:{self.session_id}:{self.user_id}"

    def _load_messages(self):
        """Load messages from storage backend."""
        if self.storage == "redis":
            self._load_from_redis()
        else:
            self._load_from_file()

    def _save_messages(self):
        """Save messages to storage backend."""
        if self.storage == "redis":
            self._save_to_redis()
        else:
            self._save_to_file()

    def _load_from_redis(self):
        """Load messages from Redis."""
        try:
            raw = self.redis_client.get(self._get_redis_key())
            if raw:
                messages_data = json.loads(raw)
                self.messages = []
                for msg in messages_data:
                    if msg["type"] == "human":
                        self.messages.append(HumanMessage(content=msg["data"]["content"]))
                    elif msg["type"] == "ai":
                        self.messages.append(AIMessage(content=msg["data"]["content"]))
                    elif msg["type"] == "system":
                        self.messages.append(SystemMessage(content=msg["data"]["content"]))
            else:
                self.messages = []
        except Exception as e:
            print(f"Error loading messages from Redis: {e}")
            self.messages = []

    def _save_to_redis(self):
        """Save messages to Redis with TTL."""
        messages_json = []
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                messages_json.append({"type": "human", "data": {"content": msg.content}})
            elif isinstance(msg, AIMessage):
                messages_json.append({"type": "ai", "data": {"content": msg.content}})
            elif isinstance(msg, SystemMessage):
                messages_json.append({"type": "system", "data": {"content": msg.content}})

        try:
            self.redis_client.setex(
                self._get_redis_key(), self.ttl, json.dumps(messages_json)
            )
        except Exception as e:
            print(f"Error saving messages to Redis: {e}")

    def _load_from_file(self):
        """Load messages from JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    messages_json = json.load(f)
                    
                self.messages = []
                for msg in messages_json:
                    if msg["type"] == "human":
                        # Support both text and text+image messages
                        if isinstance(msg["data"]["content"], list):
                            self.messages.append(HumanMessage(content=msg["data"]["content"]))
                        else:
                            self.messages.append(HumanMessage(content=msg["data"]["content"]))
                    elif msg["type"] == "ai":
                        self.messages.append(AIMessage(content=msg["data"]["content"]))
                    elif msg["type"] == "system":
                        self.messages.append(SystemMessage(content=msg["data"]["content"]))
            except (json.JSONDecodeError, FileNotFoundError):
                self.messages = []
        else:
            self.messages = []

    def _save_to_file(self):
        """Save messages to JSON file."""
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

        with open(self.file_path, "w") as f:
            json.dump(messages_json, f, indent=2)

    # -------------------------------
    # Chat history interface methods
    # -------------------------------
    def add_message(self, message):
        """Add a generic message to the store."""
        self.messages.append(message)
        self._save_messages()

    def add_user_message(self, message, image_url=None):
        """
        Add a user message, optionally with an image.
        
        Args:
            message: Text message from user
            image_url: Optional image URL to attach
        """
        if image_url:
            # Create multimodal message with text and image
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

    def clear(self):
        """Clear all messages from storage."""
        self.messages = []
        if self.storage == "redis":
            try:
                self.redis_client.delete(self._get_redis_key())
            except Exception as e:
                print(f"Error clearing Redis: {e}")
        else:
            self._save_to_file()

    # -------------------------------
    # Extra Redis session utilities
    # -------------------------------
    def save_session(self, data: dict, ttl: int = None) -> bool:
        """
        Save arbitrary session data (only for Redis storage).
        
        Args:
            data: Dictionary of session data to save
            ttl: Time-to-live in seconds (uses self.ttl if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        if self.storage != "redis":
            print("save_session is only available for Redis storage")
            return False
            
        key = f"session:{self.session_id}"
        try:
            self.redis_client.setex(key, ttl or self.ttl, json.dumps(data))
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    def get_session(self):
        """
        Retrieve arbitrary session data (only for Redis storage).
        
        Returns:
            Session data dictionary or None
        """
        if self.storage != "redis":
            print("get_session is only available for Redis storage")
            return None
            
        key = f"session:{self.session_id}"
        try:
            raw = self.redis_client.get(key)
            if raw:
                return json.loads(raw)
        except Exception as e:
            print(f"Error getting session: {e}")
        return None

    def increment_counter(self) -> int | None:
        """
        Increment counter per session (only for Redis storage).
        
        Returns:
            New counter value or None
        """
        if self.storage != "redis":
            print("increment_counter is only available for Redis storage")
            return None
            
        key = f"counter:{self.session_id}"
        try:
            return self.redis_client.incr(key)
        except Exception as e:
            print(f"Error incrementing counter: {e}")
            return None

    def exists_session(self) -> bool:
        """
        Check if session exists (only for Redis storage).
        
        Returns:
            True if session exists, False otherwise
        """
        if self.storage != "redis":
            return os.path.exists(self.file_path)
            
        key = f"session:{self.session_id}"
        try:
            return self.redis_client.exists(key) == 1
        except Exception as e:
            print(f"Error checking session existence: {e}")
            return False


# --- Demo ---
if __name__ == "__main__":
    # Test with Redis storage
    print("=== Testing Redis Storage ===")
    sid = "12345"
    uid = "user_100"
    chat_history_redis = RedisSupportChatHistory(sid, uid, storage="redis")

    chat_history_redis.add_user_message("Xin chào!", image_url=None)
    chat_history_redis.add_ai_message("Chào bạn, tôi là AI Agent.")
    chat_history_redis.add_user_message("Đây là ảnh của tôi", 
                                       image_url="data:image/png;base64,iVBORw0...")
    print("Messages:", len(chat_history_redis.messages))

    print("Save session:", chat_history_redis.save_session({"user": "baobao"}, ttl=20))
    print("Get session:", chat_history_redis.get_session())
    print("Exists session:", chat_history_redis.exists_session())
    print("Counter 1:", chat_history_redis.increment_counter())
    print("Counter 2:", chat_history_redis.increment_counter())
    
    # Test with File storage
    print("\n=== Testing File Storage ===")
    chat_history_file = RedisSupportChatHistory(sid, uid, storage="file")
    
    chat_history_file.add_user_message("Test file storage")
    chat_history_file.add_ai_message("File storage works!")
    chat_history_file.add_user_message("Image test", 
                                      image_url="https://example.com/image.jpg")
    print("Messages:", len(chat_history_file.messages))
    print("File exists:", chat_history_file.exists_session())
