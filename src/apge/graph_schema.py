from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# Schema version can be used for future migrations
SCHEMA_VERSION = "1.0"

@dataclass
class BaseNode:
    # Base class for all nodes in the graph
    # All nodes will have a schema_version field
    schema_version: str = field(default_factory=lambda: SCHEMA_VERSION)

@dataclass
class Diagnosis(BaseNode):
    name: str  # e.g., "PTSD", "Major Depressive Disorder"
    # Relationships:
    # (:Diagnosis)-[:HAS_SYMPTOM]->(:Symptom)

@dataclass
class Symptom(BaseNode):
    name: str  # e.g., "Intrusive Thoughts", "Anhedonia"
    icd_code: Optional[str] = None  # e.g., "F43.10" (for PTSD)
    # Relationships:
    # (:Symptom)-[:TARGETED_BY]->(:Target)

@dataclass
class Target(BaseNode):
    region: str  # e.g., "Left DLPFC", "Right DLPFC", "dACC", "Pre-SMA", "Left Temporoparietal Junction", "M1 (motor cortex)", "Occipital cortex"
    # MNI coordinates, e.g., (-44, 36, 20)
    mni_coords: Optional[Tuple[float, float, float]] = None
    # Relationships:
    # (:Target)-[:USUALLY_TREATED_WITH]->(:StimParams)

@dataclass
class StimParams(BaseNode):
    # Pattern of stimulation, e.g., "10 Hz", "1 Hz", "iTBS", "20 Hz (iTBS)"
    pattern: str
    pulses: int  # Number of pulses per session, e.g., 3000, 1800, 1200, 600
    # Intensity as a percentage of Motor Threshold (MT) or Active Motor Threshold (AMT)
    # Store as float, e.g., 120.0 for 120%, 80.0 for 80%
    intensity_pct: float
    # Typical number of sessions, can be a range string e.g., "20-30", "25-36" or a specific number
    sessions: str
    # Relationships:
    # (:StimParams)-[:SUPPORTED_BY]->(:Evidence)
    # Potential risky factors associated with these params could be properties or inferred
    # e.g., is_high_frequency: bool, is_high_intensity: bool (for penalty calculations)

@dataclass
class Evidence(BaseNode):
    # Level of evidence, e.g., "High", "Moderate", "Moderate-High", "Emerging", or A/B/C/...
    level: str
    # Required fields first
    references: List[str] = field(default_factory=list)  # e.g., ["George et al., 2010", "Blumberger et al., 2018"]
    # Optional fields with defaults
    effect_size: Optional[float] = None
    n_participants: Optional[int] = None
    pub_year: Optional[int] = None
    doi: Optional[str] = None # Digital Object Identifier
    title: Optional[str] = None # Title of the publication
    notes: Optional[str] = None  # Could include notes summarizing the evidence

@dataclass
class Device(BaseNode):
    name: str  # e.g., "NeoStar", "BrainsWay", "Magstim"
    manufacturer: str  # e.g., "NeoStar", "BrainsWay", "Magstim"
    coil_type: str  # e.g., "figure-8", "H-Coil"
    focality_mm: str  # e.g., "5-10mm", "Deep and broad", "Unknown"
    fda_clearance_ids: List[str] = field(default_factory=list) # e.g., ["K123456", "K789012"]
    # Relationships:
    # (:StimParams)-[:DELIVERED_BY]->(:Device)

# --- Relationships to be established in the graph ---
# (d:Diagnosis)-[:HAS_SYMPTOM]->(s:Symptom)
# (s:Symptom)-[:TARGETED_BY]->(t:Target)
# (t:Target)-[:USUALLY_TREATED_WITH]->(sp:StimParams)
# (sp:StimParams)-[:SUPPORTED_BY]->(e:Evidence)
# (sp:StimParams)-[:DELIVERED_BY]->(d:Device)

# Example of how these might be used (conceptual, not for this file):
# diagnosis_node = Diagnosis(name="Major Depressive Disorder")
# symptom_node = Symptom(name="Anhedonia")
# target_node = Target(region="Left DLPFC", mni_coords=(-44, 36, 20))
# stim_params_node = StimParams(pattern="10 Hz", pulses=3000, intensity_pct=120.0, sessions="20-30")
# evidence_node = Evidence(level="High", references=["George et al., 2010"], notes="...")
