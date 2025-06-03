// Add constraints for Device node
CREATE CONSTRAINT ON (d:Device) ASSERT d.name IS UNIQUE;
CREATE CONSTRAINT ON (d:Device) ASSERT d.manufacturer IS UNIQUE;

// Add constraint for StimParams node
CREATE CONSTRAINT ON (sp:StimParams) ASSERT sp.id IS UNIQUE;

// Backfill data for existing entries
// NeoStar
MERGE (d1:Device {name: 'NeoStar', manufacturer: 'NeoStar', coil_type: 'figure-8', focality_mm: 'Unknown', fda_clearance_ids: []});
// BrainsWay
MERGE (d2:Device {name: 'BrainsWay', manufacturer: 'BrainsWay', coil_type: 'H-Coil', focality_mm: 'Unknown', fda_clearance_ids: []});
// Magstim
MERGE (d3:Device {name: 'Magstim', manufacturer: 'Magstim', coil_type: 'figure-8', focality_mm: 'Unknown', fda_clearance_ids: []});

// Add DELIVERED_BY relationships (example, replace with actual logic)
// MATCH (sp:StimParams {protocol_id: 'some_protocol_id'}), (d:Device {name: 'NeoStar'})
// MERGE (sp)-[:DELIVERED_BY]->(d);
