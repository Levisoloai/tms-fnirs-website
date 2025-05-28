import React from 'react';

interface CardProps {
  title: string;
  abstract?: string;
  links?: Array<{ href: string; text: string }>;
  tags?: string[];
  children?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ title, abstract, links, tags, children }) => {
  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-6">
      {/* Title */}
      <div className="text-xl font-semibold text-white mb-2">{title}</div>

      {/* Abstract */}
      {abstract && (
        <p className="text-sm text-gray-300 mb-4">{abstract}</p>
      )}

      {/* Children (Custom Content) */}
      {children && <div className="mb-4">{children}</div>}

      {/* Links */}
      {links && links.length > 0 && (
        <div className="mt-4">
          {links.map((link, index) => (
            <a
              key={index}
              href={link.href}
              className="text-cyan-400 hover:text-cyan-300 mr-4 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 focus:ring-offset-gray-800 rounded-sm" // Added rounded-sm for better ring appearance
              target="_blank" // Good practice for external links
              rel="noopener noreferrer" // Security for target="_blank"
            >
              {link.text}
            </a>
          ))}
        </div>
      )}

      {/* Tags */}
      {tags && tags.length > 0 && (
        <div className="mt-4">
          {tags.map((tag, index) => (
            <span
              key={index}
              className="bg-gray-700 text-gray-300 text-xs font-medium mr-2 mb-2 inline-block px-2.5 py-0.5 rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export default Card;
