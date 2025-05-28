import type { Meta, StoryObj } from '@storybook/react';
import LiteratureEnginePagePlaceholder from './LiteratureEnginePagePlaceholder';

const meta: Meta<typeof LiteratureEnginePagePlaceholder> = {
  title: 'Pages/Placeholders/LiteratureEnginePage',
  component: LiteratureEnginePagePlaceholder,
  parameters: { layout: 'fullscreen' },
};
export default meta;
type Story = StoryObj<typeof LiteratureEnginePagePlaceholder>;
export const Default: Story = {};
