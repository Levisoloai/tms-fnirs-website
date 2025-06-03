from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple # Added Tuple for mni_coords if used later

class PatientDataInput(BaseModel):
    primaryDiagnosis: Optional[str] = Field(None, description="Primary diagnosis of the patient")
    symptoms: Optional[List[str]] = Field(default_factory=list, description="List of predominant symptoms")
    severity: Optional[str] = Field(None, description="Symptom severity")
    comorbidities: Optional[List[str]] = Field(default_factory=list, description="List of comorbid conditions")
    previousTreatments: Optional[List[str]] = Field(default_factory=list, description="List of previous treatments")
    age: Optional[str] = Field(None, description="Age of the patient") # Kept as string to match JS, consider int
    handedness: Optional[str] = Field('right', description="Patient's handedness")
    medicationResistant: Optional[bool] = Field(False, description="Is the patient medication resistant?")
    currentMedications: Optional[List[str]] = Field(default_factory=list, description="List of current medications")
    contraindicationsPresent: Optional[bool] = Field(False, description="Are potential contraindications present?")
    specificContraindications: Optional[List[str]] = Field(default_factory=list, description="List of specific contraindications")

class ProtocolDetail(BaseModel):
    target: str
    frequency: str
    intensity: str
    pulses: int
    sessions: str
    schedule: str
    evidence: str
    notes: str
    references: Optional[List[str]] = Field(default_factory=list)
    symptom: Optional[str] = None # Added to match structure if primary is symptom-specific

class RecommendationOutput(BaseModel):
    primary: Optional[ProtocolDetail] = None
    alternatives: List[ProtocolDetail] = Field(default_factory=list)
    modifications: List[str] = Field(default_factory=list)
    safetyConsiderations: List[str] = Field(default_factory=list)
    monitoring: List[str] = Field(default_factory=list)
    expectedOutcomes: Dict[str, str] = Field(default_factory=dict)
    # This field will capture any warnings, like identified contraindications.
    warnings: List[str] = Field(default_factory=list)


class TargetOutput(BaseModel):
    region: str
    # mni_coords: Optional[Tuple[float, float, float]] = None # Future enhancement

class TargetsListOutput(BaseModel):
    targets: List[TargetOutput]
