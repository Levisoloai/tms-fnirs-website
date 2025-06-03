# src/apge/api/static_data.py

diagnoses_list = [
    "Major Depressive Disorder", "Treatment-Resistant Depression", "Obsessive-Compulsive Disorder",
    "PTSD", "Schizophrenia (Auditory Hallucinations)", "Chronic Pain", "Fibromyalgia", "Migraine", "Generalized Anxiety Disorder"
]

symptoms_map = {
    "Major Depressive Disorder": ["Anhedonia", "Psychomotor Retardation", "Cognitive Impairment"],
    "Treatment-Resistant Depression": ["Severe Anhedonia", "Persistent Low Mood"],
    "Obsessive-Compulsive Disorder": ["Obsessions", "Compulsions"],
    "PTSD": ["Intrusive Thoughts", "Hyperarousal", "Avoidance Symptoms", "iTBS Left DLPFC"], # "iTBS Left DLPFC" is a protocol, but kept as symptom based on JS
    "Schizophrenia (Auditory Hallucinations)": ["Auditory Hallucinations"],
    "Chronic Pain": ["Persistent Pain", "Neuropathic Pain"],
    "Fibromyalgia": ["Widespread Pain", "Fatigue"],
    "Migraine": ["Headache Frequency", "Aura Symptoms"],
    "Generalized Anxiety Disorder": ["Excessive Worry", "Restlessness", "Muscle Tension", "1 Hz Right DLPFC"] # "1 Hz Right DLPFC" is a protocol
}

comorbidities_list = [
    "Anxiety", "Substance Use Disorder", "Insomnia", "Chronic Fatigue"
]

previous_treatments_list = [
    "SSRI", "SNRI", "TCA", "MAOI", "Psychotherapy", "ECT", "Other TMS"
]

contraindications_list = [
    "Metallic Implant", "Seizure History", "Pregnancy", "Cardiac Pacemaker"
]

# Bundle them for easier import in main.py
all_static_data_for_api = {
    "diagnoses": diagnoses_list,
    "symptoms": symptoms_map, # This is the symptoms_map for the UI, logic might need specific symptom lists
    "comorbidities": comorbidities_list,
    "previousTreatments": previous_treatments_list,
    "contraindications": contraindications_list
    # Note: The recommendation logic in main.py currently uses these list names directly
    # from the passed dictionary. If generate_recommendations_py needs more specific
    # lists (e.g. a flat list of all possible symptoms for validation), they could be added here.
}
