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

  it('does not show option buttons on initial render', () => {
    renderDropdown();
    expect(screen.queryByRole('button', { name: 'Option B' })).not.toBeInTheDocument();
  });
});

// --- Trigger button ---

describe('Dropdown trigger button', () => {
  it('is not disabled when options are provided', () => {
    renderDropdown();
    expect(screen.getByRole('button')).not.toBeDisabled();
  });
});

// --- Open / close interactions ---

describe('Dropdown open and close', () => {
  it('opens the dropdown when the trigger is clicked', async () => {
    renderDropdown();
    await userEvent.click(screen.getByRole('button'));
    expect(screen.getByRole('button', { name: 'Option B' })).toBeInTheDocument();
  });

  it('closes the dropdown when the trigger is clicked again', async () => {
    renderDropdown();
    const trigger = screen.getByRole('button');
    await userEvent.click(trigger);
    await userEvent.click(trigger);
    expect(screen.queryByRole('button', { name: 'Option B' })).not.toBeInTheDocument();
  });

  it('closes the dropdown when Escape is pressed', async () => {
    renderDropdown();
    await userEvent.click(screen.getByRole('button'));
    await userEvent.keyboard('{Escape}');
    expect(screen.queryByRole('button', { name: 'Option B' })).not.toBeInTheDocument();
  });

  it('closes the dropdown when clicking outside', async () => {
    render(
      <div>
        <Dropdown value="opt-a" options={OPTIONS} onChange={vi.fn()} />
        <button>Outside</button>
      </div>
    );
    await userEvent.click(screen.getAllByRole('button')[0]);
    expect(screen.getByRole('button', { name: 'Option B' })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Outside' }));
    expect(screen.queryByRole('button', { name: 'Option B' })).not.toBeInTheDocument();
  });

  it('does not open when there are no options', async () => {
    renderDropdown({ options: [] });
    expect(screen.getAllByRole('button')).toHaveLength(1);
    await userEvent.click(screen.getByRole('button'));
    expect(screen.getAllByRole('button')).toHaveLength(1);
  });
});

// --- Option selection ---

describe('Dropdown option selection', () => {
  it('calls onChange with the selected option value', async () => {
    const { onChange } = renderDropdown({ value: 'opt-a' });
    await userEvent.click(screen.getByRole('button'));
    await userEvent.click(screen.getByRole('button', { name: 'Option C' }));
    expect(onChange).toHaveBeenCalledWith('opt-c');
  });

  it('closes the dropdown after an option is selected', async () => {
    renderDropdown();
    await userEvent.click(screen.getByRole('button'));
    await userEvent.click(screen.getByRole('button', { name: 'Option B' }));
    expect(screen.queryByRole('button', { name: 'Option C' })).not.toBeInTheDocument();
  });
});
