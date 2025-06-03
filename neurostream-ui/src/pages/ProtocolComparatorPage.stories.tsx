import type { Meta, StoryObj } from '@storybook/react';
import ProtocolComparatorPage from './ProtocolComparatorPage';

const meta = {
  title: 'Pages/ProtocolComparatorPage',
  component: ProtocolComparatorPage,
  parameters: {
    layout: 'fullscreen',
  },
} satisfies Meta<typeof ProtocolComparatorPage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
