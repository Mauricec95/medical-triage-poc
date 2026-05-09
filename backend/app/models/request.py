"""MedicalRequest Pydantic / SQLModel schema — single source of truth."""

from datetime import UTC, datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from sqlmodel import Column, SQLModel, Text
from sqlmodel import Field as SQLField

# ── Enums ─────────────────────────────────────────────────────────────

class Modality(str, Enum):
    scanner = "scanner"
    irm = "IRM"
    doppler = "doppler"
    echo = "echo"
    radio = "radio"
    autre = "autre"


class Urgency(str, Enum):
    routine = "routine"
    prioritaire = "prioritaire"
    urgent = "urgent"


class NextAction(str, Enum):
    contact_prescriber = "contact_prescriber"
    contact_patient = "contact_patient"
    await_radiologist_validation = "await_radiologist_validation"
    schedule = "schedule"
    reject = "reject"


class Channel(str, Enum):
    email = "email"
    fax = "fax"
    portal = "portal"
    walkin = "walkin"


class RequestStatus(str, Enum):
    complet = "complet"
    incomplet = "incomplet"
    a_valider = "a_valider"
    route = "route"


# ── Sub-models (Pydantic, not persisted individually) ─────────────────

class PatientInfo(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[str] = None
    sex: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    ssn_last4_optional: Optional[str] = None


class PrescriberInfo(BaseModel):
    full_name: Optional[str] = None
    specialty: Optional[str] = None
    service: Optional[str] = None
    hospital_or_clinic: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class ExamInfo(BaseModel):
    modality: Optional[Modality] = None
    region: Optional[str] = None
    with_injection: Optional[bool] = None  # None means unknown
    protocol_notes: Optional[str] = None
    urgency: Urgency = Urgency.routine


class Attachment(BaseModel):
    name: str
    present: bool = False
    notes: Optional[str] = None


class MissingField(BaseModel):
    field_path: str
    reason: str
    suggested_question_fr: str


class Routing(BaseModel):
    next_action: NextAction = NextAction.await_radiologist_validation
    target_contact: Optional[str] = None
    rationale_fr: Optional[str] = None


class SourceInfo(BaseModel):
    channel: Channel = Channel.email
    raw_text: Optional[str] = None
    attachments_text: Optional[str] = None


# ── Main structured request ──────────────────────────────────────────

class MedicalRequest(BaseModel):
    """Full structured medical request extracted from an incoming message."""

    patient: PatientInfo = Field(default_factory=PatientInfo)
    prescriber: PrescriberInfo = Field(default_factory=PrescriberInfo)
    exam: ExamInfo = Field(default_factory=ExamInfo)
    clinical_indication: Optional[str] = None
    required_attachments: list[Attachment] = Field(default_factory=list)
    missing_fields: list[MissingField] = Field(default_factory=list)
    routing: Routing = Field(default_factory=Routing)
    ack_message_fr: Optional[str] = None
    confidence: float = 0.0
    source: SourceInfo = Field(default_factory=SourceInfo)


# ── Database model ───────────────────────────────────────────────────

class MedicalRequestDB(SQLModel, table=True):
    """Persisted version — stores the full MedicalRequest as JSON."""

    __tablename__ = "medical_requests"

    id: str = SQLField(default_factory=lambda: str(uuid4()), primary_key=True)
    status: RequestStatus = RequestStatus.a_valider
    data_json: str = SQLField(default="", sa_column=Column(Text))
    source_filename: Optional[str] = None
    created_at: datetime = SQLField(
        default_factory=lambda: datetime.now(UTC),
    )
    updated_at: datetime = SQLField(
        default_factory=lambda: datetime.now(UTC),
    )
