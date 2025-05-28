import type { Meta, StoryObj } from '@storybook/react';
import Tooltip from './Tooltip';
import Button from './Button'; // Assuming Button component exists

const meta: Meta<typeof Tooltip> = {
  title: 'UI/Tooltip',
  component: Tooltip,
  tags: ['autodocs'],
  argTypes: {
    content: { control: 'text' },
    position: {
      control: 'select',
      options: ['top', 'bottom', 'left', 'right'],
    },
    // children prop is not suitable for direct control in Storybook
    // as it expects a ReactElement. It's demonstrated via stories.
  },
  decorators: [ // Optional: Add a decorator to center the tooltip for better viewing in Storybook
    (Story) => (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px' }}>
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof Tooltip>;

export const Default: Story = {
  args: {
    content: 'This is a tooltip!',
    position: 'top',
    children: <Button>Hover or Focus me</Button>,
  },
};

export const OnText: Story = {
  args: {
    content: 'Tooltip for a span of text.',
    position: 'bottom',
    children: <span tabIndex={0} className="text-white underline decoration-dotted cursor-help">Some informative text (focusable)</span>,
    // Added tabIndex to make the span focusable for tooltip testing
  },
};

export const RightPositioned: Story = {
  args: {
    content: 'This tooltip is on the right.',
    position: 'right',
    children: <Button>Button</Button>,
  },
};

export const LeftPositioned: Story = {
  args: {
    content: 'This tooltip is on the left.',
    position: 'left',
    children: <Button>Button</Button>,
  },
};

export const LongContent: Story = {
  args: {
    content: 'This is a much longer tooltip content to see how it wraps and behaves. Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    position: 'top',
    children: <Button>Hover for Long Tooltip</Button>,
  }
}
