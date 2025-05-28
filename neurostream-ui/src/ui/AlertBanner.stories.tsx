import type { Meta, StoryObj } from '@storybook/react';
import AlertBanner from './AlertBanner';

const meta: Meta<typeof AlertBanner> = {
  title: 'UI/AlertBanner',
  component: AlertBanner,
  tags: ['autodocs'],
  argTypes: {
    message: { control: 'text' },
    type: {
      control: 'select',
      options: ['info', 'warning', 'success', 'error'],
    },
    icon: {
        control: 'object', // Or null if not providing a custom control
        description: 'Optional custom ReactNode for the icon. For complex nodes like SVGs, control is limited; shown via specific story.'
    }
  },
};
export default meta;

type Story = StoryObj<typeof AlertBanner>;

export const Info: Story = {
  args: {
    message: 'This is an informational message.',
    type: 'info',
  },
};

export const Warning: Story = {
  args: {
    message: 'This is a warning message. Be careful!',
    type: 'warning',
  },
};

export const Success: Story = {
  args: {
    message: 'Operation completed successfully.',
    type: 'success',
  },
};

export const Error: Story = {
  args: {
    message: 'An error occurred. Please try again.',
    type: 'error',
  },
};

export const WithCustomIcon: Story = {
    args: {
        message: "This alert has a custom SVG icon.",
        type: 'info',
        icon: (
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
            </svg>
        )
    }
};
