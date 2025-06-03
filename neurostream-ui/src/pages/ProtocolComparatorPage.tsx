import React, { useState, useEffect, useMemo, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import html2pdf from 'html2pdf.js';
import { useRouter } from 'next/router';

interface ProtocolCardItem {
  id: string;
  label: string;
  device?: string;
  evidence_level?: string;
}

interface ComparisonTable {
  columns: string[];
  data: any[][]; // Keeping `any` for now, can be refined if cell types are known
}

interface ComparisonData {
  table: ComparisonTable;
  narrative_md: string;
  lit_chunks?: any[]; // From backend, not used in UI yet
}

const ProtocolComparatorPage: React.FC = () => {
  const [availableProtocols, setAvailableProtocols] = useState<ProtocolCardItem[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [isLoadingList, setIsLoadingList] = useState(false);
  const [errorList, setErrorList] = useState<string | null>(null);
  const MAX_SELECTED_PROTOCOLS = 4;

  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [isLoadingCompare, setIsLoadingCompare] = useState(false);
  const [errorCompare, setErrorCompare] = useState<string | null>(null);
  const [isNarrativeVisible, setIsNarrativeVisible] = useState(true);

  // Sorting State
  const [sortConfig, setSortConfig] = useState<{ key: string | null; direction: 'ascending' | 'descending' }>({ key: null, direction: 'ascending' });

  // Filtering State
  const [filterText, setFilterText] = useState('');
  const FILTER_COLUMN_KEY = 'Coil Type'; // Default column to filter by

  const router = useRouter();
  const [isInitialURLLoadProcessed, setIsInitialURLLoadProcessed] = useState(false);
  const [isAvailableProtocolsLoaded, setIsAvailableProtocolsLoaded] = useState(false);


  // Effect for fetching available protocols
  useEffect(() => {
    const fetchProtocols = async () => {
      setIsLoadingList(true);
      setErrorList(null);
      try {
        const response = await fetch('/api/protocol/list?diagnosis=MDD-anxious');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data: ProtocolCardItem[] = await response.json();
        setAvailableProtocols(data);
        setIsAvailableProtocolsLoaded(true); // Signal that protocols are loaded
      } catch (e) {
        setErrorList(e instanceof Error ? e.message : String(e));
        setAvailableProtocols([]);
        setIsAvailableProtocolsLoaded(true); // Still signal load attempt finished
      } finally {
        setIsLoadingList(false);
      }
    };
    fetchProtocols();
  }, []);

  // Effect 1: Read IDs from URL on initial component load and when router is ready
  useEffect(() => {
    if (router.isReady && isAvailableProtocolsLoaded && !isInitialURLLoadProcessed) {
      const queryIds = router.query.ids;
      let idsToSet: string[] = [];

      if (queryIds) {
        const idsFromQueryRaw = Array.isArray(queryIds) ? queryIds[0] : queryIds;
        if (idsFromQueryRaw) { // Ensure idsFromQueryRaw is not empty string before splitting
            const idsFromQueryArr = idsFromQueryRaw.split(',');
            // Filter against available protocols to ensure validity
            idsToSet = idsFromQueryArr.filter(id => availableProtocols.some(p => p.id === id))
                                     .slice(0, MAX_SELECTED_PROTOCOLS);
        }
      }

      // Only update if the derived IDs are different from current selectedIds
      // This prevents loops if selectedIds were already set by user interaction before URL processing completed
      const sortedIdsToSet = [...idsToSet].sort().join(',');
      const sortedCurrentSelectedIds = [...selectedIds].sort().join(',');

      if (sortedIdsToSet !== sortedCurrentSelectedIds) {
        setSelectedIds(idsToSet);
      }
      setIsInitialURLLoadProcessed(true); // Mark initial URL processing as done
    }
  }, [router.isReady, router.query.ids, availableProtocols, isAvailableProtocolsLoaded, isInitialURLLoadProcessed, selectedIds]);


  // Effect 2: Update URL when selectedIds change by user interaction (after initial load)
  useEffect(() => {
    // Ensure router is ready and initial URL load has been processed
    if (!router.isReady || !isInitialURLLoadProcessed) {
      return;
    }

    const currentQueryIds = router.query.ids ? (Array.isArray(router.query.ids) ? router.query.ids[0] : router.query.ids) : '';
    const newSelectedIdsString = selectedIds.join(',');

    // Only push to router if the query param needs to change
    if (currentQueryIds !== newSelectedIdsString) {
      if (selectedIds.length > 0) {
        router.replace({
          pathname: router.pathname,
          query: { ...router.query, ids: newSelectedIdsString },
        }, undefined, { shallow: true });
      } else {
        // If no IDs are selected, remove 'ids' from query
        const newQuery = { ...router.query };
        delete newQuery.ids;
        router.replace({
          pathname: router.pathname,
          query: newQuery,
        }, undefined, { shallow: true });
      }
    }
  }, [selectedIds, router, isInitialURLLoadProcessed]); // router.isReady, router.query implicitly part of `router`


  // Effect for fetching comparison data when selectedIds change
  useEffect(() => {
    // This effect should run if selectedIds is populated either by URL or by user interaction
    if (selectedIds.length === 0) {
      setComparisonData(null);
      setErrorCompare(null);
      return;
    }

    const fetchComparison = async () => {
      setIsLoadingCompare(true);
      setErrorCompare(null);
      try {
        const response = await fetch('/api/protocol/compare', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ids: selectedIds }),
        });
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
          throw new Error(`HTTP error! status: ${response.status} - ${errorData.detail || "Failed to fetch comparison"}`);
        }
        const data: ComparisonData = await response.json();
        setComparisonData(data);
      } catch (e) {
        setErrorCompare(e instanceof Error ? e.message : String(e));
        setComparisonData(null);
      } finally {
        setIsLoadingCompare(false);
      }
    };

    fetchComparison();
  }, [selectedIds]);

  const handleSelectProtocol = (id: string) => {
    setSelectedIds(prevSelectedIds => {
      if (prevSelectedIds.includes(id)) {
        return prevSelectedIds.filter(pid => pid !== id);
      }
      if (prevSelectedIds.length < MAX_SELECTED_PROTOCOLS) {
        return [...prevSelectedIds, id];
      }
      alert(`You can select a maximum of ${MAX_SELECTED_PROTOCOLS} protocols.`);
      return prevSelectedIds;
    });
  };

  const getEvidenceColor = (level?: string) => {
    if (!level) return 'text-gray-500';
    const lowerLevel = level.toLowerCase();
    if (lowerLevel.includes('high') || lowerLevel.includes('level a')) return 'text-green-600 font-semibold';
    if (lowerLevel.includes('medium') || lowerLevel.includes('level b')) return 'text-yellow-600 font-semibold';
    if (lowerLevel.includes('low') || lowerLevel.includes('level c')) return 'text-red-600 font-semibold';
    return 'text-gray-500';
  };

  const selectedProtocolObjects = availableProtocols.filter(p => selectedIds.includes(p.id));

  const requestSort = useCallback((key: string) => {
    let direction: 'ascending' | 'descending' = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  }, [sortConfig]);

  const processedTableData = useMemo(() => {
    if (!comparisonData?.table?.data) {
      return [];
    }

    let items = [...comparisonData.table.data];

    // Sorting
    if (sortConfig.key !== null && comparisonData.table.columns) {
      const columnIndex = comparisonData.table.columns.indexOf(sortConfig.key);
      if (columnIndex !== -1) {
        items.sort((a, b) => {
          const valA = a[columnIndex];
          const valB = b[columnIndex];

          // Handle null or undefined consistently
          if (valA === null || valA === undefined) return sortConfig.direction === 'ascending' ? -1 : 1;
          if (valB === null || valB === undefined) return sortConfig.direction === 'ascending' ? 1 : -1;

          // Attempt numeric sort for known numeric-like fields if possible, otherwise string
          // For simplicity, direct comparison (works for strings, and numbers if they are actual numbers)
          // A more robust solution might inspect column name or try parseFloat
          if (valA < valB) return sortConfig.direction === 'ascending' ? -1 : 1;
          if (valA > valB) return sortConfig.direction === 'ascending' ? 1 : -1;
          return 0;
        });
      }
    }

    // Filtering
    if (filterText.trim() !== '' && comparisonData.table.columns) {
      const filterColumnIndex = comparisonData.table.columns.indexOf(FILTER_COLUMN_KEY);
      if (filterColumnIndex !== -1) {
        items = items.filter(row => {
          const cellValue = row[filterColumnIndex];
          return String(cellValue).toLowerCase().includes(filterText.toLowerCase());
        });
      }
    }
    return items;
  }, [comparisonData, sortConfig, filterText]);

  const getSortIndicator = (columnKey: string) => {
    if (sortConfig.key === columnKey) {
      return sortConfig.direction === 'ascending' ? ' \u2191' : ' \u2193'; // Up arrow / Down arrow
    }
    return '';
  };

  const handleExportToPdf = () => {
    const element = document.getElementById('comparison-export-area');
    if (!element) {
      console.error("Element to export ('comparison-export-area') not found!");
      alert("Could not export to PDF: Content area not found.");
      return;
    }

    const options = {
      margin:       [0.5, 0.5, 0.5, 0.5], // top, left, bottom, right in inches
      filename:     'neurostream_protocol_comparison.pdf',
      image:        { type: 'jpeg', quality: 0.95 },
      html2canvas:  { scale: 2, useCORS: true, logging: false },
      jsPDF:        { unit: 'in', format: 'letter', orientation: 'landscape' } // landscape for wider tables
    };

    // Temporarily make narrative visible for export if it's hidden
    const wasNarrativeHidden = !isNarrativeVisible;
    if (wasNarrativeHidden) {
      setIsNarrativeVisible(true);
    }

    // Use a short timeout to allow narrative to become visible before PDF generation
    setTimeout(() => {
      html2pdf().from(element).set(options).save().then(() => {
        if (wasNarrativeHidden) {
          setIsNarrativeVisible(false); // Restore original visibility
        }
      }).catch(err => {
        console.error("Error during PDF generation:", err);
        if (wasNarrativeHidden) {
          setIsNarrativeVisible(false); // Restore original visibility even on error
        }
      });
    }, 100); // 100ms timeout, adjust if needed
  };

  return (
    <div className="p-4 md:p-8 lg:p-12 space-y-8 bg-gray-50 min-h-screen">
      <h1 className="text-4xl font-bold text-center text-gray-800 mb-10">Protocol Comparator</h1>

      {/* Protocol Picker Section */}
      <div className="mb-10 p-6 bg-white border border-gray-200 rounded-xl shadow-lg">
        <h2 className="text-2xl font-semibold text-gray-700 mb-5">Select Protocols (Up to {MAX_SELECTED_PROTOCOLS})</h2>
        {isLoadingList && <p className="text-blue-600">Loading protocols...</p>}
        {errorList && <p className="text-red-600 bg-red-50 p-3 rounded-md">Error fetching protocols: {errorList}</p>}
        {!isLoadingList && !errorList && availableProtocols.length === 0 && (
          <p className="text-gray-500">No protocols found for "MDD-anxious".</p>
        )}
        <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {availableProtocols.map(protocol => {
            const isSelected = selectedIds.includes(protocol.id);
            const isDisabled = !isSelected && selectedIds.length >= MAX_SELECTED_PROTOCOLS;
            return (
              <li
                key={protocol.id}
                onClick={() => !isDisabled && handleSelectProtocol(protocol.id)}
                className={`p-5 border rounded-lg shadow-md hover:shadow-xl transition-all duration-300 ease-in-out transform hover:-translate-y-1
                            ${isSelected ? 'border-blue-600 ring-2 ring-blue-500 bg-blue-50 scale-105' : 'border-gray-300 bg-white'}
                            ${isDisabled ? 'opacity-60 cursor-not-allowed bg-gray-100' : 'cursor-pointer'}
                           `}
              >
                <h3 className="text-lg font-bold text-gray-900 truncate" title={protocol.label}>{protocol.label}</h3>
                <p className="text-sm text-gray-700 mt-1">Device: <span className="font-medium text-indigo-600">[Logo: {protocol.device || 'N/A'}]</span></p>
                <p className={`text-sm mt-1 ${getEvidenceColor(protocol.evidence_level)}`}>
                  Evidence: {protocol.evidence_level || 'N/A'}
                </p>
              </li>
            );
          })}
        </ul>
      </div>

      {/* Comparison Section Placeholder - "Sticky Header" */}
      {selectedIds.length > 0 && (
        <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-md p-4 mb-6 rounded-lg shadow-md border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-700 mb-3">Comparing Protocols:</h2>
          <div className="flex flex-wrap gap-3 items-center">
            {selectedProtocolObjects.map(p => (
              <div key={p.id} className="bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1.5 rounded-full shadow-sm">
                {p.label}
                {/* Placeholder for Swap/Remove - No functionality */}
                <span className="ml-2 text-blue-400 hover:text-blue-600 cursor-pointer">(Swap/Remove)</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Comparison Data Display Area */}
      <div className="space-y-8">
        {isLoadingCompare && <p className="text-center text-xl text-blue-600">Loading comparison data...</p>}
        {errorCompare && <p className="text-center text-xl text-red-600 bg-red-50 p-4 rounded-md shadow">Error loading comparison: {errorCompare}</p>}

        {!isLoadingCompare && !errorCompare && selectedIds.length > 0 && !comparisonData && (
             <p className="text-center text-xl text-gray-500">No comparison data available for the selected protocols.</p>
        )}

        {!isLoadingCompare && !errorCompare && selectedIds.length === 0 && (
             <p className="text-center text-xl text-gray-500">Select protocols above to see their comparison.</p>
        )}

        {comparisonData && (
          <>
            <div className="mb-6 flex justify-end"> {/* Button container */}
              <button
                onClick={handleExportToPdf}
                disabled={!comparisonData || processedTableData.length === 0}
                className="px-6 py-2 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Export to PDF
              </button>
            </div>

            <div id="comparison-export-area"> {/* Wrapper for PDF export content */}
              {/* Dynamic Comparison Table */}
              <div className="bg-white p-6 border border-gray-200 rounded-xl shadow-lg mb-8"> {/* Added mb-8 for spacing in PDF */}
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-semibold text-gray-700">Comparison Table</h2>
                  {/* Filter input is outside the export area, but its effect (processedTableData) is inside */}
                  <input
                    type="text"
                    placeholder={`Filter by ${FILTER_COLUMN_KEY}...`}
                    value={filterText}
                    onChange={(e) => setFilterText(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm print:hidden" // Hide filter input in PDF
                  />
                </div>
                {comparisonData.table.columns.length > 0 && processedTableData.length > 0 ? (
                  <div className="overflow-x-auto rounded-lg border border-gray-200">
                    <table className="min-w-full divide-y divide-gray-200 table-auto">
                      <thead className="bg-gray-100">
                        <tr>
                          {comparisonData.table.columns.map((column) => (
                            <th
                              key={column}
                              onClick={() => requestSort(column)}
                              // Add print:text-xs to make font smaller in PDF if needed, or manage via @media print CSS
                              className="px-6 py-3.5 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider whitespace-nowrap cursor-pointer hover:bg-gray-200 transition-colors"
                            >
                              {column}{getSortIndicator(column)}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {processedTableData.map((row, rowIndex) => (
                          <tr key={rowIndex} className={`${rowIndex % 2 === 0 ? '' : 'bg-gray-50'} hover:bg-gray-100 transition-colors`}>
                            {row.map((cell, cellIndex) => {
                              const columnName = comparisonData?.table?.columns[cellIndex];
                              const cellData = cell === null || cell === undefined ? 'N/A' : String(cell);

                              if (columnName === 'DOI' && cellData !== 'N/A' && cellData.startsWith('10.')) { // Basic DOI check
                                return (
                                  <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                    <a
                                      href={`https://doi.org/${cellData}`}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-blue-600 hover:text-blue-800 hover:underline"
                                    >
                                      {cellData}
                                    </a>
                                  </td>
                                );
                              }
                              return (
                                <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{cellData}</td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                   <p className="text-gray-500 py-4">{filterText ? `No protocols match your filter for "${filterText}" in ${FILTER_COLUMN_KEY}.` : "No data available for the comparison table or current selection."}</p>
                )}
              </div>

              {/* Dynamic Narrative Pane */}
              <div className="bg-white p-6 border border-gray-200 rounded-xl shadow-lg">
                <div className="flex justify-between items-center mb-4 print:hidden"> {/* Hide toggle button in PDF */}
                  <h2 className="text-2xl font-semibold text-gray-700">Generated Narrative</h2>
                  <button
                    onClick={() => setIsNarrativeVisible(!isNarrativeVisible)}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-colors"
                  >
                    {isNarrativeVisible ? 'Hide' : 'Show'} Narrative
                  </button>
                </div>
                {/* Narrative content itself will be included based on isNarrativeVisible state */}
                {/* html2pdf will capture it if visible. The handleExportToPdf temporarily makes it visible. */}
                {isNarrativeVisible && (
                  <div className="prose prose-sm sm:prose lg:prose-lg xl:prose-xl max-w-none p-4 bg-gray-50 rounded-md border border-gray-200">
                    <ReactMarkdown>{comparisonData.narrative_md || "No narrative generated."}</ReactMarkdown>
                  </div>
                )}
                 {/* Fallback for PDF if narrative was hidden and JS timeout trick doesn't work perfectly in all browsers for html2pdf */}
                 {!isNarrativeVisible && (
                    <div className="print:block hidden prose prose-sm sm:prose lg:prose-lg xl:prose-xl max-w-none p-4 bg-gray-50 rounded-md border border-gray-200">
                         <ReactMarkdown>{comparisonData.narrative_md || "No narrative generated."}</ReactMarkdown>
                    </div>
                 )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ProtocolComparatorPage;
