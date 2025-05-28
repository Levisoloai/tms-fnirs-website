import React, { useState } from 'react';

interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactElement; // Expect a single React element as children
  position?: 'top' | 'bottom' | 'left' | 'right'; // Optional position
}

const Tooltip: React.FC<TooltipProps> = ({ content, children, position = 'top' }) => {
  const [isVisible, setIsVisible] = useState(false);

  const showTooltip = () => setIsVisible(true);
  const hideTooltip = () => setIsVisible(false);

  const childWithHandlers = React.cloneElement(children, {
    ...children.props, // Pass through existing props
    onMouseEnter: showTooltip,
    onMouseLeave: hideTooltip,
    onFocus: showTooltip,
    onBlur: hideTooltip,
    // Add ARIA attributes for accessibility if desired (e.g., aria-describedby)
  });

  let positionClasses = '';
  switch (position) {
    case 'top':
      positionClasses = 'bottom-full left-1/2 -translate-x-1/2 mb-2';
      break;
    case 'bottom':
      positionClasses = 'top-full left-1/2 -translate-x-1/2 mt-2';
      break;
    case 'left':
      positionClasses = 'right-full top-1/2 -translate-y-1/2 mr-2';
      break;
    case 'right':
      positionClasses = 'left-full top-1/2 -translate-y-1/2 ml-2';
      break;
    default:
      positionClasses = 'bottom-full left-1/2 -translate-x-1/2 mb-2'; // Default to top
  }

  return (
    <div className="relative inline-block">
      {childWithHandlers}
      {isVisible && (
        <div
          role="tooltip"
          className={`absolute z-10 px-3 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg shadow-sm ${positionClasses}`}
          // Using simplified styling without opacity transition for now
        >
          {content}
        </div>
      )}
    </div>
  );
};

export default Tooltip;
