import type { Meta, StoryObj } from '@storybook/react';
import ProtocolToolWrapper from './ProtocolToolWrapper';

const meta: Meta<typeof ProtocolToolWrapper> = {
  title: 'UI/ProtocolToolWrapper',
  component: ProtocolToolWrapper,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
  },
};
export default meta;

type Story = StoryObj<typeof ProtocolToolWrapper>;

export const Default: Story = {
  args: {
    children: (
      <>
        <div className="bg-gray-700 p-4 rounded-lg md:w-1/2"> {/* Left Column Placeholder */}
          <h2 className="text-white text-lg font-semibold">Patient Form Area</h2>
          <p className="text-gray-300">Form inputs would go here...</p>
        </div>
        <div className="bg-gray-700 p-4 rounded-lg md:w-1/2 mt-4 md:mt-0"> {/* Right Column Placeholder */}
          <h2 className="text-white text-lg font-semibold">Recommendation Panel</h2>
          <p className="text-gray-300">Results and explanations would go here...</p>
        </div>
      </>
    ),
  },
};
