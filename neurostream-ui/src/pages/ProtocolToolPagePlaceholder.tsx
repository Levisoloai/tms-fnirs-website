import React from 'react';
import TMSProtocolTool from '../../components/TMSProtocolTool/TMSProtocolTool'; // Adjusted path

const ProtocolToolPagePlaceholder: React.FC = () => {
  return (
    // The entire content of this page is now the TMSProtocolTool component.
    // The previous two-column layout is removed in favor of TMSProtocolTool's own layout.
    <TMSProtocolTool />
  );
};

export default ProtocolToolPagePlaceholder;
