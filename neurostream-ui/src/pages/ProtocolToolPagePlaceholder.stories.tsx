import type { Meta, StoryObj } from '@storybook/react';
import ProtocolToolPagePlaceholder from './ProtocolToolPagePlaceholder';

const meta: Meta<typeof ProtocolToolPagePlaceholder> = {
  title: 'Pages/Placeholders/ProtocolToolPage',
  component: ProtocolToolPagePlaceholder,
  parameters: { layout: 'fullscreen' },
};
export default meta;
type Story = StoryObj<typeof ProtocolToolPagePlaceholder>;
export const Default: Story = {};
