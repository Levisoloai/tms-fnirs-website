import type { Preview } from '@storybook/react';
import '../src/index.css'; // Import Tailwind's CSS
import { initialize, mswLoader } from 'msw-storybook-addon';

// Initialize MSW
initialize({
  onUnhandledRequest: 'bypass', // or 'warn'
});

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    // msw parameter should be configured in individual stories or globally here if needed
    // For now, individual stories will provide their handlers.
  },
  loaders: [mswLoader], // Add mswLoader to enable the addon
};

export default preview;