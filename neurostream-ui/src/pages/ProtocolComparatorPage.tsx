import React from 'react';

// Dummy data for the comparator
const dummyComparatorData = {
  table: {
    columns: ["Protocol", "Coil Type", "Frequency", "Intensity", "Pulses", "Sessions", "Evidence"],
    data: [
      ["Protocol Alpha", "Figure-8", "10 Hz", "120% RMT", "3000", "20", "Level A"],
      ["Protocol Beta", "H-Coil", "20 Hz", "110% RMT", "2000", "30", "Level B"],
    ],
  },
  narrative_md: `## Comparison Narrative

This is a **dummy narrative** for the protocol comparison.

### Coil Physics
Protocol Alpha uses a Figure-8 coil, while Protocol Beta uses an H-Coil.

### Session Burden
Protocol Alpha involves 20 sessions, whereas Protocol Beta involves 30 sessions.

### Evidence Strength
Protocol Alpha has Level A evidence, and Protocol Beta has Level B evidence.

**Clinical Pearl:** Consider patient preference when choosing between these protocols.
`
};

const ProtocolComparatorPage: React.FC = () => {
  return (
    <div>
      <h1>Protocol Comparator</h1>

      {/* Display selected IDs (dummy) */}
      <div>
        <h2>Selected Protocols:</h2>
        <ul>
          <li>Protocol Alpha (ID: p1_dummy)</li>
          <li>Protocol Beta (ID: p2_dummy)</li>
        </ul>
      </div>

      {/* Display table */}
      <div>
        <h2>Comparison Table</h2>
        <table>
          <thead>
            <tr>
              {dummyComparatorData.table.columns.map((column) => (
                <th key={column}>{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {dummyComparatorData.table.data.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Display narrative */}
      <div>
        <h2>Narrative</h2>
        <div style={{ border: '1px solid #ccc', padding: '10px', whiteSpace: 'pre-wrap' }}>
          {dummyComparatorData.narrative_md}
        </div>
      </div>
    </div>
  );
};

export default ProtocolComparatorPage;
