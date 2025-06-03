// neurostream-ui/src/mocks/handlers.ts
import { http, HttpResponse } from 'msw'; // Using msw v2+ syntax

const mockProtocolsList = [
  { id: 'p1', label: 'Alpha Protocol (Mock)', device: 'Device A', evidence_level: 'High' },
  { id: 'p2', label: 'Beta Protocol (Mock)', device: 'Device B', evidence_level: 'Medium' },
  { id: 'p3', label: 'Gamma Protocol (Mock)', device: 'Device A', evidence_level: 'High' },
  { id: 'p4', label: 'Delta Protocol (Mock)', device: 'Device C', evidence_level: 'Low' },
  { id: 'p5', label: 'Epsilon Protocol (Mock)', device: 'Device B', evidence_level: 'Medium' },
];

const mockComparisonData = (protocolIds: string[]) => ({
  table: {
    columns: [
        "Protocol Name", "Coil Type", "Frequency", "Intensity",
        "Pulses/Session", "Sessions", "Evidence Level", "Device Name",
        "Manufacturer", "Publication Title", "Publication Year", "DOI"
    ],
    data: protocolIds.map(id => {
        const protocol = mockProtocolsList.find(p => p.id === id);
        // Generate mock citation data based on protocol ID
        let mockTitle = `Study on ${protocol ? protocol.label : id}`;
        let mockYear = 2020 + (parseInt(id.substring(1)) % 4); // e.g., p1 -> 2021, p2 -> 2022
        let mockDoi = `10.1000/mock-${id}-${mockYear}`;
        let mockManufacturer = protocol?.device === 'Device A' ? 'Mfg A' : (protocol?.device === 'Device B' ? 'Mfg B' : 'Mfg C');

        return [
            `${protocol ? protocol.label : id + ' Name'} (Mocked Data)`, // Protocol Name
            id === 'p1' || id === 'p3' ? 'Figure-8 (Mock)' : 'H-Coil (Mock)', // Coil Type
            id === 'p1' ? '10 Hz (Mock)' : 'iTBS (Mock)', // Frequency
            id === 'p1' ? '120% rMT (Mock)' : '110% rMT (Mock)', // Intensity
            id === 'p1' ? 3000 : (id === 'p2' ? 1800 : 2400), // Pulses/Session
            id === 'p1' ? 20 : (id === 'p2' ? 30 : 25), // Sessions
            protocol?.evidence_level || 'N/A', // Evidence Level
            protocol?.device || 'N/A', // Device Name
            mockManufacturer, // Manufacturer
            mockTitle, // Publication Title
            mockYear, // Publication Year
            mockDoi,  // DOI
        ];
    })
  },
  narrative_md: `## Mock Narrative for ${protocolIds.join(', ')}
This is a **mock comparison narrative** based on the selected IDs.
- Protocol ${protocolIds[0] || 'N/A'} often uses a Figure-8 coil for more focal stimulation.
- Protocol ${protocolIds[1] || (protocolIds.length > 1 ? 'N/A' : (protocolIds.length === 1 ? 'N/A' : 'Another protocol'))} might involve more sessions, increasing patient burden but potentially offering different efficacy.
Clinical Pearl: Always cross-reference mock data with real-world clinical guidelines.`,
  lit_chunks: []
});

export const handlers = [
  http.get('/api/protocol/list', ({ request }) => {
    const url = new URL(request.url);
    const diagnosis = url.searchParams.get('diagnosis');
    // console.log('MSW: /api/protocol/list called with diagnosis:', diagnosis);
    // You could filter mockProtocolsList based on diagnosis if needed for more realistic mocks
    return HttpResponse.json(mockProtocolsList);
  }),

  http.post('/api/protocol/compare', async ({ request }) => {
    const body = await request.json() as { ids: string[] };
    // console.log('MSW: /api/protocol/compare called with IDs:', body.ids);
    if (!body.ids || body.ids.length === 0) {
      return HttpResponse.json({
        table: { columns: [], data: [] },
        narrative_md: 'No IDs provided for mock comparison.',
        lit_chunks: []
      }, { status: 400 }); // Return 400 for bad request if no IDs
    }
    return HttpResponse.json(mockComparisonData(body.ids));
  }),
];
