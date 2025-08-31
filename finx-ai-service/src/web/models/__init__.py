# Import all models and their table instances
from .users import User, UserModel, Users
from .auths import Auth, AuthModel, Auths
from .chats import Chat, ChatModel, Chats, Folder, FolderModel, Folders
from .groups import Group, GroupModel, Groups
from .channels import Channel, ChannelModel, Channels
from .messages import Message, MessageModel, Messages, MessageReaction, MessageReactionModel, MessageReactions
from .files import File, FileModel, Files
from .models import Model, ModelModel, Models
from .tags import Tag, TagModel, Tags
from .memories import Memory, MemoryModel, Memories
from .feedback import Feedback, FeedbackModel, Feedbacks
from .knowledge import Knowledge, KnowledgeModel, Knowledges
from .prompts import Prompt, PromptModel, Prompts
from .connections import Connection, ConnectionModel, Connections, ConnectionTemplate, ConnectionTemplateModel, ConnectionLog, ConnectionLogModel

# Export all models and table instances
__all__ = [
    # SQLAlchemy Models
    "User", "Auth", "Chat", "Folder", "Group", "Channel", "Message", "MessageReaction",
    "File", "Model", "Tag", "Memory", "Feedback", "Knowledge", "Prompt", "Connection",
    "ConnectionTemplate", "ConnectionLog",

    # Pydantic Models
    "UserModel", "AuthModel", "ChatModel", "FolderModel", "GroupModel", "ChannelModel",
    "MessageModel", "MessageReactionModel", "FileModel", "ModelModel", "TagModel",
    "MemoryModel", "FeedbackModel", "KnowledgeModel", "PromptModel", "ConnectionModel",
    "ConnectionTemplateModel", "ConnectionLogModel",

    # Table Instances
    "Users", "Auths", "Chats", "Folders", "Groups", "Channels", "Messages", "MessageReactions",
    "Files", "Models", "Tags", "Memories", "Feedbacks", "Knowledges", "Prompts", "Connections"
]
