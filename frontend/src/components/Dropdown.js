//This component provides a dropdown selector. 
//This was built for selecting different types of charts but has been updated to be usable for anything.  

import React, { useState, useRef, useEffect } from 'react';
import './Dropdown.css';

//This component takes the current value, the function that changes the current value, and the list of options (as an array) as parameters
//List of options provided must at least include a "value" element for each option, and a "label" which is what will be displayed in the dropdown menu
//See chart selection dropdown in Dashboard.js for usage example 
const Dropdown = ({ value, onChange, options }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    // Closes dropdown if clicks anywhere outside of the dropdown
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (option) => {
    onChange(option.value);
    setIsOpen(false);
  };

  //Set option state to provided option from function call. Fall back to first possible option if any errors. 
  const selectedOption = options.find(opt => opt.value === value) || options[0];

  return (
    <div className="chart-dropdown" ref={dropdownRef}> {/* we use this ref to detect if we've clicked outside of the dropdown (to close it)*/}
      <button 
        type="button"
        onClick={() => setIsOpen(!isOpen)} 
        className="chart-dropdown-trigger"
      >
        <span className="chart-dropdown-text">{selectedOption.label}</span> {/* show the name of the current option in the box if the dropdown is closed */}
        <span className={`chart-dropdown-arrow ${isOpen ? 'open' : ''}`}>▼</span> {/* if we append open to the class name, we trigger a 180 degree rotation of the arrow (see css) */}
      </button>
      
      {/* render only if isOpen is true */}
      {isOpen && (  
        <div className="chart-dropdown-menu">
          {options.map((option) => ( //loop through the array to map the options to the list
            <button
              key={option.value} // assign key name for each list item to be the same as the value of the current item in the array (e.g. "pie")
              className={`chart-dropdown-option ${option.value === value ? 'selected' : ''}`} 
              onClick={() => handleSelect(option)}
              type="button"
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