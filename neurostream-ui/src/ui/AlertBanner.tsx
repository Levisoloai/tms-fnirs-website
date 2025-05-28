import React from 'react';

type AlertType = 'info' | 'warning' | 'success' | 'error';

interface AlertBannerProps {
  message: string;
  type: AlertType;
  icon?: React.ReactNode; // Optional custom icon
}

const AlertBanner: React.FC<AlertBannerProps> = ({ message, type, icon }) => {
  const typeStyles = {
    info: {
      bg: 'bg-teal-700', // Electric teal family
      text: 'text-teal-100',
      iconText: 'text-teal-300', // Brighter teal for icon
      iconDefault: '[i]',
    },
    warning: {
      bg: 'bg-yellow-500', // Warm yellow
      text: 'text-black', // Changed from text-yellow-900 for better contrast
      iconText: 'text-yellow-800', // Darkened icon text slightly for consistency
      iconDefault: '[!]',
    },
    success: {
      bg: 'bg-emerald-600', // Green variant
      text: 'text-emerald-100',
      iconText: 'text-emerald-300',
      iconDefault: '[✓]',
    },
    error: {
      bg: 'bg-red-600', // Red variant
      text: 'text-red-100',
      iconText: 'text-red-300',
      iconDefault: '[x]',
    },
  };

  const currentStyle = typeStyles[type];

  return (
    <div className={`p-4 rounded-md flex items-center ${currentStyle.bg}`}>
      {/* Icon Area */}
      <div className={`mr-3 font-bold ${currentStyle.iconText}`}>
        {icon || currentStyle.iconDefault}
      </div>

      {/* Message Area */}
      <div className={`text-sm font-medium ${currentStyle.text}`}>
        {message}
      </div>
    </div>
  );
};

export default AlertBanner;
