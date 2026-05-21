"""Core domain enumerations for the Meeting Protocol module."""

from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    SECRETARY = "secretary"
    CHAIRMAN = "chairman"
    USER = "user"


class MeetingLevel(StrEnum):
    STRATEGIC = "strategic"
    COORDINATION = "coordination"
    OPERATIONAL = "operational"
    SITUATIONAL = "situational"


class MeetingStatus(StrEnum):
    PREPARATION = "preparation"
    IN_PROGRESS = "in_progress"
    ON_APPROVAL = "on_approval"
    APPROVED = "approved"


class WorkflowStage(StrEnum):
    TO_DO = "to_do"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    COMPLETED = "completed"


class RaciRole(StrEnum):
    R = "R"
    A = "A"
    C = "C"
    I = "I"





class OrgRole(StrEnum):
    CLIENT = "client"
    GENERAL_CONTRACTOR = "general_contractor"
    SUBCONTRACTOR = "subcontractor"
    SUPPLIER = "supplier"

class ParticipantRole(StrEnum):
    CHAIRMAN = "chairman"
    SECRETARY = "secretary"
    PARTICIPANT = "participant"