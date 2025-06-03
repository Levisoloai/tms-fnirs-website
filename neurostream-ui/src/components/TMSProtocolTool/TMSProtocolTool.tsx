import React, { useState, useEffect } from 'react';

// Placeholder Icon Components (can be replaced with actual icons later)
const Brain = () => <span className="mr-2">🧠</span>; // Emoji placeholder
const Activity = () => <span className="mr-2">⚡️</span>;
const Zap = () => <span className="mr-2">⚡</span>;
const ListChecks = () => <span className="mr-2">✅</span>;
const AlertTriangle = () => <span className="mr-2">⚠️</span>;
const BookOpen = () => <span className="mr-2">📚</span>;
const Info = () => <span className="mr-2">ℹ️</span>;

// Data (moved from tms_protocol_tool.html)
const diagnoses = [
    "Major Depressive Disorder", "Treatment-Resistant Depression", "Obsessive-Compulsive Disorder",
    "PTSD", "Schizophrenia (Auditory Hallucinations)", "Chronic Pain", "Fibromyalgia", "Migraine", "Generalized Anxiety Disorder"
];

const symptoms: { [key: string]: string[] } = {
    "Major Depressive Disorder": ["Anhedonia", "Psychomotor Retardation", "Cognitive Impairment"],
    "Treatment-Resistant Depression": ["Severe Anhedonia", "Persistent Low Mood"],
    "Obsessive-Compulsive Disorder": ["Obsessions", "Compulsions"],
    "PTSD": ["Intrusive Thoughts", "Hyperarousal", "Avoidance Symptoms", "iTBS Left DLPFC"],
    "Schizophrenia (Auditory Hallucinations)": ["Auditory Hallucinations"],
    "Chronic Pain": ["Persistent Pain", "Neuropathic Pain"],
    "Fibromyalgia": ["Widespread Pain", "Fatigue"],
    "Migraine": ["Headache Frequency", "Aura Symptoms"],
    "Generalized Anxiety Disorder": ["Excessive Worry", "Restlessness", "Muscle Tension", "1 Hz Right DLPFC"]
};

const comorbidities = ["Anxiety", "Substance Use Disorder", "Insomnia", "Chronic Fatigue"];
const previousTreatments = ["SSRI", "SNRI", "TCA", "MAOI", "Psychotherapy", "ECT", "Other TMS"];
const contraindications = ["Metallic Implant", "Seizure History", "Pregnancy", "Cardiac Pacemaker"];

// protocolDatabase is now fetched from API
// const protocolDatabase: any = {
// 'Major Depressive Disorder': {
// 'Anhedonia': {
// 'target': 'Left DLPFC', 'frequency': '10 Hz', 'intensity': '120% MT', 'pulses': 3000,
// ... (rest of the old hardcoded data)
// }
// };
            'sessions': '20-30', 'schedule': 'Daily (5x/week)', 'evidence': 'High',
            'notes': 'High-frequency stimulation of left DLPFC shows strong evidence for anhedonia improvement',
            'references': ['George et al., 2010', 'Blumberger et al., 2018']
        },
        'Psychomotor Retardation': {
            'target': 'Left DLPFC + Right DLPFC (sequential)', 'frequency': '10 Hz (L) / 1 Hz (R)',
            'intensity': '120% MT', 'pulses': 3000, 'sessions': '25-36', 'schedule': 'Daily (5x/week)',
            'evidence': 'Moderate-High',
            'notes': 'Bilateral stimulation may be more effective for psychomotor symptoms',
            'references': ["O'Reardon et al., 2007"]
        },
        'Cognitive Impairment': {
            'target': 'Left DLPFC', 'frequency': '20 Hz (iTBS)', 'intensity': '80% AMT', 'pulses': 1800,
            'sessions': '20-30', 'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
            'notes': 'iTBS may provide cognitive benefits with shorter treatment times',
            'references': ['Blumberger et al., 2018']
        }
    },
    'Treatment-Resistant Depression': {
        'Severe Anhedonia': {
            'target': 'Bilateral DLPFC', 'frequency': '10 Hz (L) / 1 Hz (R)', 'intensity': '120% MT',
            'pulses': 4000, 'sessions': '30-36', 'schedule': 'Daily (5x/week) + maintenance',
            'evidence': 'High',
            'notes': 'Extended course with maintenance sessions recommended for TRD'
        }
    },
    'Obsessive-Compulsive Disorder': {
        'Obsessions': {
            'target': 'Right DLPFC or dACC', 'frequency': '1 Hz (low) or 10 Hz (high)',
            'intensity': '110% MT', 'pulses': 1800, 'sessions': '20-30',
            'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
            'notes': 'Both inhibitory and excitatory protocols show promise'
        },
        'Compulsions': {
            'target': 'Pre-SMA or OFC', 'frequency': '1 Hz', 'intensity': '110% MT', 'pulses': 1200,
            'sessions': '25-30', 'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
            'notes': 'Targeting motor control areas may reduce compulsive behaviors'
        }
    },
    'PTSD': {
        'Intrusive Thoughts': {
            'target': 'Right DLPFC', 'frequency': '1 Hz', 'intensity': '110% MT', 'pulses': 1200,
            'sessions': '20-25', 'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
            'notes': 'Inhibitory stimulation of right DLPFC may reduce hyperarousal'
        },
        'iTBS Left DLPFC': {
            'target': 'Left DLPFC', 'frequency': 'iTBS', 'intensity': '80% AMT', 'pulses': 600,
            'sessions': '20', 'schedule': 'Daily (5x/week)', 'evidence': 'Emerging',
            'notes': 'Intermittent TBS shows promise in PTSD symptom reduction',
            'references': ['Osuch et al., 2009']
        }
    },
    'Schizophrenia (Auditory Hallucinations)': {
        'Auditory Hallucinations': {
            'target': 'Left Temporoparietal Junction', 'frequency': '1 Hz', 'intensity': '90% MT',
            'pulses': 1200, 'sessions': '20-30', 'schedule': 'Daily (5x/week)',
            'evidence': 'Moderate-High',
            'notes': 'Low-frequency stimulation of auditory areas shows good efficacy'
        }
    },
    'Chronic Pain': {
        'Persistent Pain': {
            'target': 'M1 (motor cortex)', 'frequency': '10 Hz', 'intensity': '80-90% MT',
            'pulses': 2000, 'sessions': '15-20', 'schedule': 'Daily (5x/week)',
            'evidence': 'Moderate',
            'notes': 'Motor cortex stimulation for central pain processing'
        }
    },
    'Fibromyalgia': {
        'Widespread Pain': {
            'target': 'M1 (motor cortex)', 'frequency': '10 Hz', 'intensity': '80% MT',
            'pulses': 1600, 'sessions': '20-25', 'schedule': '3-5x/week', 'evidence': 'Moderate',
            'notes': 'Lower intensity may be better tolerated in fibromyalgia patients'
        }
    },
    'Migraine': {
      'Headache Frequency': {
        'target': 'Occipital cortex or M1', 'frequency': '1 Hz or 10 Hz', 'intensity': '90% MT',
        'pulses': 1200, 'sessions': '12-20', 'schedule': '3x/week', 'evidence': 'Moderate',
        'notes': 'Both excitatory and inhibitory protocols show preventive effects'
      }
    },
    'Generalized Anxiety Disorder': {
      'Excessive Worry': {
        'target': 'Left DLPFC', 'frequency': '10 Hz', 'intensity': '110% MT', 'pulses': 2000,
        'sessions': '20-30', 'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
        'notes': 'Standard high-frequency protocol for GAD'
      },
      'Restlessness': {
        'target': 'Right DLPFC', 'frequency': '1 Hz', 'intensity': '120% MT', 'pulses': 1200,
        'sessions': '20-30', 'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
        'notes': 'Low-frequency right DLPFC may help restlessness'
      },
      '1 Hz Right DLPFC': {
        'target': 'Right DLPFC', 'frequency': '1 Hz', 'intensity': '120% MT', 'pulses': 1200,
        'sessions': '20-30', 'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
        'notes': 'Low-frequency right DLPFC stimulation reduces anxiety symptoms',
        'references': ['Mantovani et al., 2013']
      }
    }
};

interface PatientData {
    diagnosis: string;
    symptoms: string[];
    comorbidities: string[];
    previousTreatments: string[];
    contraindications: string[];
    [key: string]: any; // For additional dynamic fields like age, mdd_duration
}

interface Recommendation {
    symptom: string;
    protocol: any; // Can be more specific later
    adjustments?: string[];
}

// Define a type for the protocol data fetched from the API
type ApiProtocolData = { [key: string]: any } | null;

const TMSProtocolTool: React.FC = () => {
    const [patientData, setPatientData] = useState<PatientData>({
        diagnosis: "",
        symptoms: [],
        comorbidities: [],
        previousTreatments: [],
        contraindications: []
    });
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [showResults, setShowResults] = useState(false);

    // State for API data, loading, and error handling
    const [apiProtocolData, setApiProtocolData] = useState<ApiProtocolData>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchProtocols = async () => {
            setIsLoading(true);
            setError(null); // Clear previous errors
            try {
                const response = await fetch('http://localhost:8000/protocols'); // Ensure API is running
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                setApiProtocolData(data);
            } catch (e: any) {
                console.error("Failed to fetch protocols:", e);
                setError(e.message);
                setApiProtocolData(null); // Clear any stale data
            } finally {
                setIsLoading(false);
            }
        };

        fetchProtocols();
    }, []); // Empty dependency array means this runs once on mount

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = event.target;
        setPatientData(prev => ({ ...prev, [name]: value }));
        if (name === "diagnosis") {
            // Reset symptoms when diagnosis changes
            setPatientData(prev => ({ ...prev, symptoms: [] }));
        }
    };

    const handleMultiSelect = (event: React.ChangeEvent<HTMLSelectElement>, field: keyof PatientData) => {
        const options = Array.from(event.target.selectedOptions, option => option.value);
        setPatientData(prev => ({ ...prev, [field]: options }));
    };

    const handleSymptomChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        handleMultiSelect(event, "symptoms");
    };

    const generateRecommendations = () => {
        if (!apiProtocolData) {
            // Data not loaded yet or error occurred
            setRecommendations([{ symptom: "N/A", protocol: { notes: "Protocol data is not available. Please try again later." } }]);
            setShowResults(true);
            return;
        }

        const { diagnosis, symptoms: patientSymptoms, comorbidities: patientComorbidities, previousTreatments: patientPrevTreatments, contraindications: patientContraindications } = patientData;
        let newRecommendations: Recommendation[] = [];

        if (diagnosis && apiProtocolData[diagnosis]) {
            patientSymptoms.forEach(symptom => {
                if (apiProtocolData[diagnosis][symptom]) {
                    let protocol = { ...apiProtocolData[diagnosis][symptom] };
                    let adjustments: string[] = [];

                    // Example adjustments (can be expanded)
                    if (patientComorbidities.includes("Anxiety") && protocol.target === "Left DLPFC") {
                        adjustments.push("Consider lower intensity or shorter duration due to anxiety comorbidity.");
                    }
                    if (patientPrevTreatments.includes("ECT") && protocol.intensity) {
                        adjustments.push("May require motor threshold re-assessment post-ECT.");
                    }
                    if (patientContraindications.length > 0) {
                        adjustments.push(`Review contraindications: ${patientContraindications.join(', ')} before proceeding.`);
                    }
                     if (parseInt(patientData.age || "0") > 65 && protocol.intensity) {
                        adjustments.push("Consider age: potential need for intensity adjustment or closer monitoring.");
                    }


                    newRecommendations.push({ symptom, protocol, adjustments });
                } else {
                    newRecommendations.push({ symptom, protocol: { notes: "No specific protocol found for this symptom in the selected diagnosis." } });
                }
            });
        } else {
            newRecommendations.push({ symptom: "N/A", protocol: { notes: "No protocols found for this diagnosis." } });
        }
        setRecommendations(newRecommendations);
        setShowResults(true);
    };

    const currentSymptoms = patientData.diagnosis ? symptoms[patientData.diagnosis] || [] : [];

    if (isLoading) {
        return (
            <div className="container mx-auto p-6 bg-gray-900 text-white font-sans text-center">
                <h1 className="text-3xl font-bold text-blue-400">Loading Protocol Data...</h1>
                <p className="text-xl text-gray-400 mt-2">Please wait while we fetch the latest TMS protocols.</p>
                 {/* You could add a spinner icon here */}
            </div>
        );
    }

    if (error) {
        return (
            <div className="container mx-auto p-6 bg-gray-900 text-white font-sans text-center">
                <h1 className="text-3xl font-bold text-red-500">Error Loading Data</h1>
                <p className="text-xl text-gray-400 mt-2">Failed to fetch protocol data: {error}</p>
                <p className="text-lg text-gray-500 mt-4">Please ensure the API server is running at http://localhost:8000/protocols and try refreshing the page.</p>
            </div>
        );
    }

    if (!apiProtocolData) {
         return (
            <div className="container mx-auto p-6 bg-gray-900 text-white font-sans text-center">
                <h1 className="text-3xl font-bold text-yellow-500">No Protocol Data</h1>
                <p className="text-xl text-gray-400 mt-2">Protocol data could not be loaded or is empty.</p>
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6 bg-gray-900 text-white font-sans">
            <header className="text-center mb-10">
                <h1 className="text-5xl font-bold text-blue-400">TMS Protocol Generator</h1>
                <p className="text-xl text-gray-400 mt-2">Evidence-based TMS protocol recommendations</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
                {/* Patient Input Section */}
                <div className="bg-gray-800 p-8 rounded-lg shadow-2xl">
                    <h2 className="text-3xl font-semibold mb-6 text-blue-300 flex items-center"><Brain /> Patient Information</h2>
                    <div className="space-y-5">
                        <div>
                            <label htmlFor="diagnosis" className="block text-lg mb-1 text-gray-300">Primary Diagnosis:</label>
                            <select id="diagnosis" name="diagnosis" value={patientData.diagnosis} onChange={handleInputChange} className="w-full p-3 bg-gray-700 rounded-md border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none">
                                <option value="">Select Diagnosis</option>
                                {diagnoses.map(d => <option key={d} value={d}>{d}</option>)}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="symptoms" className="block text-lg mb-1 text-gray-300">Primary Symptoms (select all that apply):</label>
                            <select id="symptoms" name="symptoms" multiple value={patientData.symptoms} onChange={handleSymptomChange} className="w-full p-3 h-32 bg-gray-700 rounded-md border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none">
                                {currentSymptoms.map(s => <option key={s} value={s}>{s}</option>)}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="age" className="block text-sm font-medium text-gray-300">Age (Years):</label>
                            <input type="number" name="age" id="age" value={patientData.age || ""} onChange={handleInputChange} className="mt-1 block w-full p-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"/>
                        </div>
                        <div>
                            <label htmlFor="comorbidities" className="block text-lg mb-1 text-gray-300">Comorbidities (select all that apply):</label>
                            <select id="comorbidities" name="comorbidities" multiple value={patientData.comorbidities} onChange={(e) => handleMultiSelect(e, "comorbidities")} className="w-full p-3 h-24 bg-gray-700 rounded-md border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none">
                                {comorbidities.map(c => <option key={c} value={c}>{c}</option>)}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="previousTreatments" className="block text-lg mb-1 text-gray-300">Significant Previous Treatments:</label>
                            <select id="previousTreatments" name="previousTreatments" multiple value={patientData.previousTreatments} onChange={(e) => handleMultiSelect(e, "previousTreatments")} className="w-full p-3 h-24 bg-gray-700 rounded-md border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none">
                                {previousTreatments.map(t => <option key={t} value={t}>{t}</option>)}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="contraindications" className="block text-lg mb-1 text-gray-300">Contraindications:</label>
                            <select id="contraindications" name="contraindications" multiple value={patientData.contraindications} onChange={(e) => handleMultiSelect(e, "contraindications")} className="w-full p-3 h-24 bg-gray-700 rounded-md border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none">
                                {contraindications.map(ci => <option key={ci} value={ci}>{ci}</option>)}
                            </select>
                        </div>
                    </div>
                    <button onClick={generateRecommendations} className="mt-8 w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg text-lg transition duration-150 ease-in-out transform hover:scale-105 flex items-center justify-center">
                        <Activity /> Generate Recommendations
                    </button>
                </div>

                {/* Results Display Section */}
                <div className="bg-gray-800 p-8 rounded-lg shadow-2xl">
                    <h2 className="text-3xl font-semibold mb-6 text-green-300 flex items-center"><Zap /> Protocol Recommendations</h2>
                    {showResults && recommendations.length > 0 ? (
                        <div className="space-y-6">
                            {recommendations.map((rec, index) => (
                                <div key={index} className="bg-gray-700 p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
                                    <h3 className="text-2xl font-semibold text-green-400 mb-3">{rec.symptom}</h3>
                                    {rec.protocol && Object.entries(rec.protocol).map(([key, value]) => {
                                        if (key === 'references' && Array.isArray(value)) {
                                            return (
                                                <div key={key} className="mb-2">
                                                    <strong className="capitalize text-gray-300">{key}:</strong>
                                                    <ul className="list-disc list-inside ml-4 text-gray-400">
                                                        {value.map((ref, i) => <li key={i}>{ref}</li>)}
                                                    </ul>
                                                </div>
                                            );
                                        }
                                        return (
                                            <p key={key} className="text-gray-300 mb-1">
                                                <strong className="capitalize text-gray-400">{key.replace('_', ' ')}:</strong> {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                            </p>
                                        );
                                    })}
                                    {rec.adjustments && rec.adjustments.length > 0 && (
                                        <div className="mt-4 p-3 bg-yellow-700 bg-opacity-30 rounded border border-yellow-500">
                                            <h4 className="text-lg font-semibold text-yellow-300 flex items-center"><AlertTriangle /> Adjustments & Considerations:</h4>
                                            <ul className="list-disc list-inside ml-4 text-yellow-200 mt-1">
                                                {rec.adjustments.map((adj, i) => <li key={i}>{adj}</li>)}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-10">
                             <Info />
                            <p className="text-gray-400 text-lg">Recommendations will appear here once patient data is submitted.</p>
                        </div>
                    )}
                </div>
            </div>

            {/* General Notes & Disclaimer */}
            <footer className="mt-12 border-t border-gray-700 pt-8 text-center">
                <div className="bg-gray-800 p-6 rounded-lg shadow-xl mb-6">
                    <h3 className="text-2xl font-semibold text-blue-300 mb-3 flex items-center justify-center"><ListChecks /> General Considerations</h3>
                    <ul className="list-disc list-inside text-gray-400 space-y-1 text-left mx-auto max-w-2xl">
                        <li>Always verify Motor Threshold (MT) and adjust intensity as needed.</li>
                        <li>Consider patient comfort and previous TMS experience.</li>
                        <li>Protocols may need adjustment based on clinical judgment and patient response.</li>
                        <li>Refer to the latest clinical guidelines and device manuals.</li>
                    </ul>
                </div>
                <div className="bg-red-800 bg-opacity-70 p-6 rounded-lg shadow-xl">
                     <h3 className="text-2xl font-semibold text-red-300 mb-3 flex items-center justify-center"><AlertTriangle /> Disclaimer</h3>
                    <p className="text-red-200">This tool is for informational purposes only and does not constitute medical advice. All treatment decisions must be made by qualified healthcare professionals.</p>
                </div>
                 <p className="text-gray-500 text-sm mt-8">&copy; 2024 NeuroStream Solutions. All rights reserved.</p>
            </footer>
        </div>
    );
};

export default TMSProtocolTool;

// Helper function for title casing (if needed elsewhere, move to utils)
// const titleCase = (str: string) => str.toLowerCase().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
