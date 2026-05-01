import React, { useState, useRef, useEffect } from 'react';

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
    ref={dropdownRef}
    className="relative inline-block min-w-0 shrink isolate"
  >
    <button
      type="button"
      onClick={() => {
        if (!hasOptions) return;
        setIsOpen(!isOpen);
      }}
      className="flex items-center justify-between gap-2 min-w-10 max-w-full px-3 py-2 text-[14px] font-bold rounded-lg border transition-all duration-200 bg-transparent text-text-muted border-brand-blue/12 hover:bg-surface-2/45 hover:border-brand-blue/35 hover:text-text-strong focus:outline-none focus:border-brand-blue/60 focus:shadow-[0_0_0_2px_rgb(var(--brand-blue)/0.25)]"
    >
      <span className="flex-1 text-left truncate min-w-0">
        {selectedLabel}
      </span>

      <span
        className={`text-[12px] shrink-0 transition-transform duration-200 ${
          isOpen ? "rotate-180" : ""
        } text-text-muted`}
      >
        ▼
      </span>
    </button>

    {isOpen && hasOptions && (
      <div
        className="absolute top-full left-0 right-0 mt-1 rounded-lg border overflow-hidden z-1100 transition-all duration-300 bg-surface-2 border-brand-blue/6 shadow-[0_18px_45px_rgb(0_0_0/0.6)]"
      >
        {safeOptions.map((option) => (
          <button
            key={option.value}
            onClick={() => handleSelect(option)}
            type="button"
            className={`w-full text-left px-4 py-3 text-[14px] transition-all duration-200 border-b last:border-b-0 text-text-muted border-brand-blue/12 hover:bg-surface-2/45 hover:text-text-strong ${
              option.value === value
                ? "bg-brand-blue/12 font-medium hover:bg-brand-blue/18"
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