from pydantic import BaseModel
from typing import Optional


# --- User Schemas ---

class UserCreate(BaseModel):
    name: str
    birth_date: str          # "1996-06-20"
    birth_time: str          # "14:00"
    birth_city: str          # "Rancagua, Chile"
    current_city: str        # "Rancagua, Chile"
    language: str = "es"
    report_depth: str = "complete"  # basic | complete | professional
    llm_model: str = "gemini-2.5-flash"


class UserResponse(BaseModel):
    id: int
    name: str
    birth_date: str
    birth_time: str
    birth_city: str
    current_city: str
    language: str
    report_depth: str
    llm_model: str
    created_at: str


class UserUpdate(BaseModel):
    current_city: Optional[str] = None
    language: Optional[str] = None
    report_depth: Optional[str] = None
    llm_model: Optional[str] = None


# --- Reading Schemas ---

class ReadingResponse(BaseModel):
    id: int
    user_id: int
    reading_type: str
    chart_data_json: str
    interpretation: str
    location_used: str
    created_at: str


# --- Request Schemas ---

class NatalChartRequest(BaseModel):
    user_id: int


class TransitRequest(BaseModel):
    user_id: int
    location: Optional[str] = None       # Override current_city
    datetime_override: Optional[str] = None  # Override "now"


class SynastryRequest(BaseModel):
    user_id_1: int
    user_id_2: Optional[int] = None      # Si se compara con otro usuario registrado
    guest_name: Optional[str] = None     # Si se compara con un invitado
    guest_birth_date: Optional[str] = None
    guest_birth_time: Optional[str] = None
    guest_birth_city: Optional[str] = None
    location_override: Optional[str] = None
