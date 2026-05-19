"""Core domain enumerations for the Meeting Protocol module."""

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    SECRETARY = "secretary"
    CHAIRMAN = "chairman"
    USER = "user"


class MeetingLevel(str, Enum):
    STRATEGIC = "strategic"
    COORDINATION = "coordination"
    OPERATIONAL = "operational"
    SITUATIONAL = "situational"


class MeetingStatus(str, Enum):
    PREPARATION = "preparation"
    IN_PROGRESS = "in_progress"
    ON_APPROVAL = "on_approval"
    APPROVED = "approved"


class WorkflowStage(str, Enum):
    TO_DO = "to_do"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    COMPLETED = "completed"


class RaciRole(str, Enum):
    R = "R"
    A = "A"
    C = "C"
    I = "I"


class ParticipantRole(str, Enum):
    CHAIRMAN = "chairman"
    SECRETARY = "secretary"
    PARTICIPANT = "participant"