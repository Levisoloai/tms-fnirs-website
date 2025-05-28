import React from 'react';

interface ProtocolToolWrapperProps {
  children: React.ReactNode; // Expecting two direct children for the two-column layout
}

const ProtocolToolWrapper: React.FC<ProtocolToolWrapperProps> = ({ children }) => {
  return (
    <div className="p-4 md:p-6 md:flex md:space-x-6">
      {children}
    </div>
  );
};

export default ProtocolToolWrapper;
