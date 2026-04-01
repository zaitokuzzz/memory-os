from enum import Enum


class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    KNOWLEDGE = "knowledge"
    BEHAVIOR = "behavior"
    BROWSER = "browser"


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PENDING_EMBEDDING = "pending_embedding"
    PENDING_DISTILL = "pending_distill"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    UNVERIFIED = "unverified"
    CONTRADICTORY = "contradictory"


class QueryType(str, Enum):
    TEMPORAL = "temporal"
    CONTEXTUAL_RECALL = "contextual_recall"
    CONCEPTUAL = "conceptual"
    FACTUAL = "factual"
    PERSONAL = "personal"
    EXTERNAL_RECENT = "external_recent"
    HYBRID = "hybrid"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
