"""Database models for the AutoAudit backend API."""

from app.models.user import User, Role
from app.models.m365_connection import M365Connection
from app.models.azure_connection import AzureConnection
from app.models.gcp_connection import GCPConnection
from app.models.aws_connection import AWSConnection
from app.models.platform import Platform
from app.models.scan_result import ScanResult
from app.models.compliance import Scan
from app.models.evidence_validation import EvidenceValidation
from app.models.contact import ContactSubmission, SubmissionNote, SubmissionHistory

__all__ = [
    "User",
    "Role",
    "M365Connection",
    "AzureConnection",
    "GCPConnection",
    "AWSConnection",
    "Platform",
    "ScanResult",
    "Scan",
    "EvidenceValidation",
    "ContactSubmission",
    "SubmissionNote",
    "SubmissionHistory",
]
