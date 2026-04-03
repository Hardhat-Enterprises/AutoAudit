//This component provides a dropdown selector. 
//This was built for selecting different types of charts but has been updated to be usable for anything.  

import React, { useState, useRef, useEffect } from 'react';

//This component takes the current value, the function that changes the current value, and the list of options (as an array) as parameters
//List of options provided must at least include a "value" element for each option, and a "label" which is what will be displayed in the dropdown menu
//See chart selection dropdown in Dashboard.js for usage example 
//Updated to support theme switching
const Dropdown = ({ value, onChange, options, isDarkMode = true }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const safeOptions = Array.isArray(options) ? options : [];
  const hasOptions = safeOptions.length > 0;

  useEffect(() => {
    // Closes dropdown if clicks anywhere outside of the dropdown
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const handleSelect = (option) => {
    onChange(option.value);
    setIsOpen(false);
  };

  //Set option state to provided option from function call. Fall back to first possible option if any errors. 
  const selectedOption = safeOptions.find(opt => opt.value === value) || safeOptions[0];
  const selectedLabel = selectedOption?.label ?? 'No options';
  return (
  <div ref={dropdownRef} className="relative w-full">
    <button
      type="button"
      onClick={() => {
        if (!hasOptions) return;
        setIsOpen(!isOpen);
      }}
      className={`w-full flex items-center justify-between px-4 py-2 rounded-lg transition ${
  isDarkMode
    ? "bg-gray-800 text-white hover:bg-gray-700"
    : "bg-white text-black hover:bg-gray-200"
}`}
      aria-haspopup="listbox"
      aria-expanded={isOpen}
      disabled={!hasOptions}
    >
      <span>{selectedLabel}</span>
      <span className={`ml-2 transition-transform ${isOpen ? 'rotate-180' : ''}`}>
        ▼
      </span>
    </button>
    {isOpen && hasOptions && (
      <div className={`absolute mt-2 w-full rounded-lg shadow-lg z-10 ${
  isDarkMode ? "bg-gray-800 text-white" : "bg-white text-black"
}`}>
        {safeOptions.map((option) => (
          <button
            key={option.value}
            onClick={() => handleSelect(option)}
            type="button"
            role="option"
            aria-selected={option.value === value}
            className={`block w-full text-left px-4 py-2 ${
  isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-200"
} ${
  option.value === value
    ? isDarkMode
      ? "bg-gray-700 font-semibold"
      : "bg-gray-300 font-semibold"
    : ""
}`}
          >
            {option.label}
          </button>
        ))}
      </div>
    )}
  </div>
);
};
export default Dropdown;
