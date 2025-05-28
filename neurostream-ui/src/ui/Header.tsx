import React from 'react';

// For now, no props are needed, but this can be expanded later.
// interface HeaderProps {}

const Header: React.FC /* <HeaderProps> */ = () => {
  return (
    <header className="bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <span className="text-2xl font-bold text-white">NeuroStream</span>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-4">
            <a
              href="#"
              className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 focus:ring-offset-gray-900"
            >
              Literature
            </a>
            <a
              href="#"
              className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 focus:ring-offset-gray-900"
            >
              Protocol Tool
            </a>
            <a
              href="#"
              className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 focus:ring-offset-gray-900"
            >
              About
            </a>
          </nav>

          {/* Dark Mode Toggle Placeholder */}
          <div className="hidden md:block">
            <button
              type="button"
              className="bg-gray-700 text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 focus:ring-offset-gray-700"
            >
              Toggle Dark
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center">
            <button
              type="button"
              className="bg-gray-700 text-gray-300 hover:text-white inline-flex items-center justify-center p-2 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 focus:ring-offset-gray-700"
              aria-controls="mobile-menu"
              aria-expanded="false" // This would be dynamic with state in a real app
            >
              <span className="sr-only">Open main menu</span>
              {/* Icon when menu is closed (e.g., hamburger) - Placeholder */}
              <svg className="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7" />
              </svg>
              {/* Icon when menu is open (e.g., X) - Placeholder for future state */}
              {/* <svg className="hidden h-6 w-6" ... > <path ... /> </svg> */}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu, show/hide based on state (placeholder for future state management) */}
      {/* For now, it's always hidden or not implemented as per "Full mobile menu functionality will be handled later" */}
      {/* <div className="md:hidden" id="mobile-menu">
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          <a href="#" className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Literature</a>
          <a href="#" className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Protocol Tool</a>
          <a href="#" className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium">About</a>
        </div>
        <div className="pt-4 pb-3 border-t border-gray-700">
          <button type="button" className="w-full text-left bg-gray-700 text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
            Toggle Dark
          </button>
        </div>
      </div> */}
    </header>
  );
};

export default Header;
