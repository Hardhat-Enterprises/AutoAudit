import React from 'react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Dropdown from './Dropdown';

const OPTIONS = [
  { value: 'opt-a', label: 'Option A' },
  { value: 'opt-b', label: 'Option B' },
  { value: 'opt-c', label: 'Option C' },
];

function renderDropdown(
  overrides: Partial<React.ComponentProps<typeof Dropdown>> = {}
) {
  const onChange = overrides.onChange ?? vi.fn();
  render(
    <Dropdown
      value={overrides.value ?? 'opt-a'}
      options={overrides.options ?? OPTIONS}
      onChange={onChange}
      isDarkMode={overrides.isDarkMode ?? true}
    />
  );
  return { onChange };
}

afterEach(cleanup);

// --- Rendering ---

describe('Dropdown rendering', () => {
  it('displays the label of the currently selected option', () => {
    renderDropdown({ value: 'opt-b' });
    expect(screen.getByText('Option B')).toBeInTheDocument();
  });

  it('defaults to the first option when value does not match any option', () => {
    renderDropdown({ value: 'no-match' });
    expect(screen.getByText('Option A')).toBeInTheDocument();
  });

  it('shows "No options" label when the options array is empty', () => {
    renderDropdown({ options: [] });
    expect(screen.getByText('No options')).toBeInTheDocument();
  });

  it('applies the "dark" class when isDarkMode is true', () => {
    const { container } = render(
      <Dropdown value="opt-a" options={OPTIONS} onChange={vi.fn()} isDarkMode={true} />
    );
    expect(container.firstChild).toHaveClass('dark');
  });

  it('applies the "light" class when isDarkMode is false', () => {
    const { container } = render(
      <Dropdown value="opt-a" options={OPTIONS} onChange={vi.fn()} isDarkMode={false} />
    );
    expect(container.firstChild).toHaveClass('light');
  });

  it('does not show the listbox on initial render', () => {
    renderDropdown();
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });
});

// --- Trigger button ---

describe('Dropdown trigger button', () => {
  it('has aria-expanded false when closed', () => {
    renderDropdown();
    expect(screen.getByRole('button')).toHaveAttribute('aria-expanded', 'false');
  });

  it('is disabled when no options are provided', () => {
    renderDropdown({ options: [] });
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('is not disabled when options are provided', () => {
    renderDropdown();
    expect(screen.getByRole('button')).not.toBeDisabled();
  });
});

// --- Open / close interactions ---

describe('Dropdown open and close', () => {
  it('opens the listbox when the trigger is clicked', async () => {
    renderDropdown();
    await userEvent.click(screen.getByRole('button'));
    expect(screen.getByRole('listbox')).toBeInTheDocument();
  });

  it('sets aria-expanded to true when open', async () => {
    renderDropdown();
    await userEvent.click(screen.getByRole('button'));
    expect(screen.getByRole('button', { expanded: true })).toBeInTheDocument();
  });

  it('shows all options in the listbox when open', async () => {
    renderDropdown();
    await userEvent.click(screen.getByRole('button'));
    const optionButtons = screen.getAllByRole('option');
    expect(optionButtons).toHaveLength(OPTIONS.length);
  });

  it('closes the listbox when the trigger is clicked again', async () => {
    renderDropdown();
    await userEvent.click(screen.getByRole('button'));
    await userEvent.click(screen.getByRole('button'));
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });

  it('closes the listbox when Escape is pressed', async () => {
    renderDropdown();
    await userEvent.click(screen.getByRole('button'));
    await userEvent.keyboard('{Escape}');
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });

  it('closes the listbox when clicking outside the dropdown', async () => {
    const { container } = render(
      <div>
        <Dropdown value="opt-a" options={OPTIONS} onChange={vi.fn()} />
        <button>Outside</button>
      </div>
    );
    await userEvent.click(container.querySelector('.chart-dropdown-trigger')!);
    expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Outside' }));
    expect(container.querySelector('[role="listbox"]')).not.toBeInTheDocument();
  });

  it('does not open when the trigger is disabled (empty options)', async () => {
    renderDropdown({ options: [] });
    await userEvent.click(screen.getByRole('button'));
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });
});

// --- Option selection ---

describe('Dropdown option selection', () => {
  it('calls onChange with the selected option value', async () => {
    const { onChange } = renderDropdown({ value: 'opt-a' });
    await userEvent.click(screen.getByRole('button'));
    await userEvent.click(screen.getByRole('option', { name: 'Option C' }));
    expect(onChange).toHaveBeenCalledWith('opt-c');
  });

  it('closes the listbox after an option is selected', async () => {
    renderDropdown();
    await userEvent.click(screen.getByRole('button'));
    await userEvent.click(screen.getByRole('option', { name: 'Option B' }));
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });

  it('marks the current value as aria-selected in the listbox', async () => {
    renderDropdown({ value: 'opt-b' });
    await userEvent.click(screen.getByRole('button'));
    expect(screen.getByRole('option', { name: 'Option B' })).toHaveAttribute(
      'aria-selected',
      'true'
    );
    expect(screen.getByRole('option', { name: 'Option A' })).toHaveAttribute(
      'aria-selected',
      'false'
    );
  });
});
