//This component provides a dropdown selector. 
//This was built for selecting different types of charts but has been updated to be usable for anything.  

import React, { useState, useRef, useEffect } from 'react';
import './Dropdown.css';

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
    <div className={`chart-dropdown ${isDarkMode ? 'dark' : 'light'}`} ref={dropdownRef}> {/* we use this ref to detect if we've clicked outside of the dropdown (to close it)*/}
      <button 
        type="button"
        onClick={() => {
          if (!hasOptions) return;
          setIsOpen(!isOpen);
        }}
        className="chart-dropdown-trigger"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        disabled={!hasOptions}
      >
        <span className="chart-dropdown-text">{selectedLabel}</span> {/* show the name of the current option in the box if the dropdown is closed */}
        <span className={`chart-dropdown-arrow ${isOpen ? 'open' : ''}`}>▼</span> {/* if we append open to the class name, we trigger a 180 degree rotation of the arrow (see css) */}
      </button>
      
      {/* render only if isOpen is true */}
      {isOpen && hasOptions && (  
        <div className="chart-dropdown-menu" role="listbox">
          {safeOptions.map((option) => ( //loop through the array to map the options to the list
            <button
              key={option.value} // assign key name for each list item to be the same as the value of the current item in the array (e.g. "pie")
              className={`chart-dropdown-option ${option.value === value ? 'selected' : ''}`} 
              onClick={() => handleSelect(option)}
              type="button"
              role="option"
              aria-selected={option.value === value}
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
