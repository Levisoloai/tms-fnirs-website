import type { Meta, StoryObj } from '@storybook/react';
import DataTable from './DataTable';

const meta: Meta<typeof DataTable> = {
  title: 'UI/DataTable',
  component: DataTable,
  tags: ['autodocs'],
  argTypes: {
    itemsPerPage: {
      control: { type: 'number', min: 1, step: 1 },
      description: 'Number of items to display per page.',
    },
    // Note: 'columns' and 'data' are complex and typically not well-suited for Storybook controls.
    // Their structure is best demonstrated via different stories.
  },
};
export default meta;

type Story = StoryObj<typeof DataTable>;

const sampleColumns = [
  { key: 'id', header: 'ID', sortable: true },
  { key: 'name', header: 'Name', sortable: true },
  { key: 'email', header: 'Email' }, // Not sortable
  { key: 'age', header: 'Age', sortable: true },
];

const sampleData = [
  { id: 1, name: 'Alice Wonderland', email: 'alice@example.com', age: 30 },
  { id: 2, name: 'Bob The Builder', email: 'bob@example.com', age: 45 },
  { id: 3, name: 'Charlie Brown', email: 'charlie@example.com', age: 22 },
  { id: 4, name: 'Diana Prince', email: 'diana@example.com', age: 28 },
  { id: 5, name: 'Edward Scissorhands', email: 'edward@example.com', age: 35 },
  { id: 6, name: 'Fiona Apple', email: 'fiona@example.com', age: 42 },
  { id: 7, name: 'George Harrison', email: 'george@example.com', age: 50 },
  { id: 8, name: 'Hannah Montana', email: 'hannah@example.com', age: 18 },
  { id: 9, name: 'Isaac Newton', email: 'isaac@example.com', age: 66 },
  { id: 10, name: 'Julia Child', email: 'julia@example.com', age: 55 },
];

export const Default: Story = {
  args: {
    columns: sampleColumns,
    data: sampleData,
    // Uses default itemsPerPage (5) from the component
  },
};

export const Paginated: Story = {
  args: {
    columns: sampleColumns,
    data: sampleData,
    itemsPerPage: 3,
  },
};

export const InitiallySorted: Story = {
  // Storybook's args system doesn't easily allow setting initial internal state like `sortConfig`
  // without a more complex wrapper component or Storybook decorators that interact with the component's state.
  // This story will demonstrate the table with a specific itemsPerPage, and sorting will be user-interactive.
  // To show a table *already sorted* by a specific column on load in Storybook,
  // you could pre-sort the `data` prop passed to it for that specific story, e.g.:
  // data: [...sampleData].sort((a, b) => a.name.localeCompare(b.name)), // Example: sorted by name
  args: {
    columns: sampleColumns,
    data: [...sampleData].sort((a,b) => b.age - a.age), // Example: Pre-sorted by age descending for demonstration
    itemsPerPage: 4,
  },
};

export const EmptyData: Story = {
  args: {
    columns: sampleColumns,
    data: [],
    itemsPerPage: 3,
  },
};

export const FewItemsNoPagination: Story = {
  args: {
    columns: sampleColumns,
    data: sampleData.slice(0,2), // Only 2 items
    itemsPerPage: 3,
  }
};
