"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


# Request Schemas
class SculptureTaskRequest(BaseModel):
    """Request to generate a sculpture for a single driver."""
    year: int = Field(..., ge=2018, le=2030, description="F1 season year")
    round: int = Field(..., ge=1, le=25, description="Race round number")
    session: str = Field(..., pattern="^(FP1|FP2|FP3|Q|R|S|SS|SQ)$", description="Session identifier")
    driver: str = Field(..., min_length=3, max_length=3, description="Driver abbreviation (e.g., VER, HAM)")


class CompareTaskRequest(BaseModel):
    """Request to compare multiple drivers."""
    year: int = Field(..., ge=2018, le=2030)
    round: int = Field(..., ge=1, le=25)
    session: str = Field(..., pattern="^(FP1|FP2|FP3|Q|R|S|SS|SQ)$")
    drivers: List[str] = Field(..., min_items=2, max_items=5, description="List of driver abbreviations")


# Response Schemas
class TaskResponse(BaseModel):
    """Response when a task is submitted."""
    task_id: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskStatusResponse(BaseModel):
    """Task status and progress information."""
    task_id: str
    status: str  # PENDING, PROGRESS, SUCCESS, FAILURE
    stage: Optional[str] = None  # loading_session, extracting_telemetry, processing_sculpture
    progress: Optional[int] = None  # 0-100
    message: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None


# Sculpture Data Schemas
class VertexData(BaseModel):
    """Single vertex in the sculpture path."""
    x: float
    y: float
    z: float
    distance: float
    speed: float
    gForce: float
    longG: float
    latG: float


class ColorData(BaseModel):
    """RGB color for a vertex."""
    r: float = Field(..., ge=0.0, le=1.0)
    g: float = Field(..., ge=0.0, le=1.0)
    b: float = Field(..., ge=0.0, le=1.0)


class SculptureMetadata(BaseModel):
    """Sculpture statistics and metadata."""
    maxGForce: float
    avgGForce: float
    maxSpeed: float
    totalDistance: float


class DriverInfo(BaseModel):
    """Driver information for a sculpture."""
    abbreviation: str
    lapTime: str
    compound: Optional[str] = None


class SculptureData(BaseModel):
    """Complete sculpture data structure."""
    vertices: List[Dict]
    colors: List[Dict]
    metadata: SculptureMetadata
    driver: DriverInfo
    generated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# Event/Session Schemas
class EventInfo(BaseModel):
    """F1 event information."""
    round: int
    name: str
    location: str
    country: str
    date: str


class SessionInfo(BaseModel):
    """Session information."""
    name: str
    fullName: str
    date: str


class DriverMetadata(BaseModel):
    """Driver metadata from a session."""
    abbreviation: str
    number: str
    fullName: str
    teamName: str
    teamColor: str


# Health Check Schema
class HealthCheckResponse(BaseModel):
    """Health check status."""
    api: str
    redis: str
    celery: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
