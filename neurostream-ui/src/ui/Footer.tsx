import React from 'react';

// No props are needed for this component currently.
// interface FooterProps {}

const Footer: React.FC /* <FooterProps> */ = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Social Media Links Placeholder */}
        <div className="flex justify-center space-x-6 mb-4">
          <a href="#" className="text-gray-400 hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 focus:ring-offset-gray-900 rounded-sm">
            [Facebook]
          </a>
          <a href="#" className="text-gray-400 hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 focus:ring-offset-gray-900 rounded-sm">
            [Twitter]
          </a>
          <a href="#" className="text-gray-400 hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 focus:ring-offset-gray-900 rounded-sm">
            [LinkedIn]
          </a>
        </div>

        {/* Copyright Text */}
        <div className="text-center text-sm text-gray-400">
          © {currentYear} NeuroStream Labs. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
