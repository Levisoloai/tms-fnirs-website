import React from 'react';

const ProtocolToolPagePlaceholder: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex p-4 space-x-4">
      {/* Left Column: Patient Form */}
      <div className="w-1/3 bg-gray-800 p-6 rounded-lg">
        <h2 className="text-2xl font-semibold mb-4 text-gray-100">
          Patient Form Inputs
        </h2>
        <p className="text-gray-400">
          This area will contain form fields for patient data, history,
          symptoms, etc.
        </p>
        {/* Placeholder for form elements */}
      </div>

      {/* Right Column: Recommendation Panel */}
      <div className="w-2/3 bg-gray-800 p-6 rounded-lg">
        <h2 className="text-2xl font-semibold mb-4 text-gray-100">
          Recommendations Area
        </h2>
        <p className="text-gray-400">
          This area will display AI-generated protocol recommendations,
          evidence, and confidence scores.
        </p>
        {/* Placeholder for recommendation elements */}
      </div>
    </div>
  );
};

export default ProtocolToolPagePlaceholder;
