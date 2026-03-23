import React, { useState, useRef, useEffect } from 'react';
import './Dropdown.css';

// Define type for each option
type Option = {
  value: string;
  label: string;
};

// Define props type
type DropdownProps = {
  value: string;
  onChange: (value: string) => void;
  options: Option[];
  isDarkMode?: boolean;
};

const Dropdown: React.FC<DropdownProps> = ({
  value,
  onChange,
  options,
  isDarkMode = true,
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);

  const safeOptions = Array.isArray(options) ? options : [];
  const hasOptions = safeOptions.length > 0;

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
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

  const handleSelect = (option: Option) => {
    onChange(option.value);
    setIsOpen(false);
  };

  const selectedOption =
    safeOptions.find((opt) => opt.value === value) || safeOptions[0];

  const selectedLabel = selectedOption?.label ?? 'No options';

  return (
    <div
      className={`chart-dropdown ${isDarkMode ? 'dark' : 'light'}`}
      ref={dropdownRef}
    >
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
        <span className="chart-dropdown-text">{selectedLabel}</span>
        <span
          className={`chart-dropdown-arrow ${isOpen ? 'open' : ''}`}
        >
          ▼
        </span>
      </button>

      {isOpen && hasOptions && (
        <div className="chart-dropdown-menu" role="listbox">
          {safeOptions.map((option) => (
            <button
              key={option.value}
              className={`chart-dropdown-option ${
                option.value === value ? 'selected' : ''
              }`}
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