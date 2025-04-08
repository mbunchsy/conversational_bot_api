from enum import Enum

class ConversationStatus(Enum):
    ACTIVE = "active"            
    COMPLETED = "completed"     
    PENDING_REVIEW = "pending_review"
    FAILED = "failed"
    ARCHIVED = "archived"
    DELETED = "deleted"
    