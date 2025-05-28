import type { Meta, StoryObj } from '@storybook/react';
import Header from './Header';

const meta: Meta<typeof Header> = {
  title: 'UI/Header',
  component: Header,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
  },
};
export default meta;

type Story = StoryObj<typeof Header>;

export const Default: Story = {
  args: {},
};

// Story to demonstrate mobile view
// This often requires configuring viewports in .storybook/preview.js or using an addon
// For now, this story just renders the component, and responsiveness can be tested via browser devtools
// or by configuring Storybook's viewport addon if available in the environment.
export const MobileView: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'mobile1', // Example: 'mobile1' is often a default in viewport addon
    },
  },
  args: {},
};
