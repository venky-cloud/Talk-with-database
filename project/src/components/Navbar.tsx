import { useState } from 'react';

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);

  // Add scroll listener
  if (typeof window !== 'undefined') {
    window.addEventListener('scroll', () => {
      setIsScrolled(window.scrollY > 20);
    });
  }

  return (
    <nav className={`fixed w-full z-50 transition-all duration-300 ${
      isScrolled ? 'glass-effect' : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center group"></div>
          <div className="flex items-center space-x-4"></div>
        </div>
      </div>
    </nav>
  );
}