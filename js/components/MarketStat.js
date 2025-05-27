export function MarketStat({ years, values, label = "Market Trend" }) {
  if (!values || values.length === 0) {
    return document.createTextNode("Market data not available.");
  }

  const maxVal = Math.max(...values);
  const minVal = Math.min(...values); // For normalization if needed, or to set baseline
  const range = maxVal - minVal;

  // SVG dimensions - can be adjusted
  const svgWidth = 100; // Increased width for better visual
  const svgHeight = 25; // Increased height
  const padding = 2; // Padding around the line

  // Calculate points for the polyline
  // X coordinates are evenly spaced
  // Y coordinates are scaled to fit svgHeight, inverted (0,0 is top-left)
  const points = values
    .map((v, i) => {
      const x =
        (i / (values.length - 1 || 1)) * (svgWidth - 2 * padding) + padding;
      // Normalize value: (value - minVal) / range. If range is 0, all points are middle.
      const normalizedY = range === 0 ? 0.5 : (v - minVal) / range;
      const y = svgHeight - (normalizedY * (svgHeight - 2 * padding) + padding);
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");

  const svg = `
    <svg 
      width='${svgWidth}' 
      height='${svgHeight}' 
      viewBox='0 0 ${svgWidth} ${svgHeight}' 
      aria-label='${label}' 
      role='img' 
      focusable='false'
      style='display: inline-block; vertical-align: middle;'
    >
      <title>${label}</title>
      <polyline
        fill='none'
        stroke='currentColor' 
        stroke-width='1.5' 
        points='${points}'
      />
    </svg>
  `;

  const wrapper = document.createElement("span");
  wrapper.className = "market-sparkline"; // Class for potential styling
  wrapper.innerHTML = svg;
  return wrapper;
}
