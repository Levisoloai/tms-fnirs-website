import type { Meta, StoryObj } from '@storybook/react';
import LandingPagePlaceholder from './LandingPagePlaceholder';

const meta: Meta<typeof LandingPagePlaceholder> = {
  title: 'Pages/Placeholders/LandingPage',
  component: LandingPagePlaceholder,
  parameters: {
    layout: 'fullscreen', // Or 'padded' if preferred
  },
};
export default meta;
type Story = StoryObj<typeof LandingPagePlaceholder>;
export const Default: Story = {};
