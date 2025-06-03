import type { Meta, StoryObj } from '@storybook/react';
import ProtocolComparatorPage from './ProtocolComparatorPage';
import { http, HttpResponse } from 'msw'; // For overriding handlers
import { handlers as mockApiHandlers } from '../mocks/handlers'; // Import your default handlers

const meta = {
  title: 'Pages/ProtocolComparatorPage',
  component: ProtocolComparatorPage,
  parameters: {
    layout: 'fullscreen',
    msw: { // Pass the default handlers to the msw parameter for all stories
      handlers: mockApiHandlers
    }
  },
} satisfies Meta<typeof ProtocolComparatorPage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const DefaultView: Story = {
  name: "Default View (with Mock Data)"
};

export const LoadingList: Story = {
  name: "Loading Protocol List",
  parameters: {
    msw: {
      handlers: [
        http.get('/api/protocol/list', () => {
          // Simulate a long delay by returning a promise that never resolves quickly
          return new Promise(resolve => setTimeout(() => resolve(HttpResponse.json([])), 300000));
        }),
        // Keep other handlers from mockApiHandlers if they exist and are needed
        ...mockApiHandlers.filter(handler => {
            const handlerInfo = (handler as any).info; // Type assertion to access info
            return handlerInfo && handlerInfo.path && !String(handlerInfo.path).startsWith('/api/protocol/list');
        })
      ]
    }
  }
};

export const ErrorList: Story = {
  name: "Error Fetching Protocol List",
  parameters: {
    msw: {
      handlers: [
        http.get('/api/protocol/list', () => {
          return HttpResponse.json({ message: 'Simulated server error fetching list' }, { status: 500 });
        }),
        ...mockApiHandlers.filter(handler => {
            const handlerInfo = (handler as any).info;
            return handlerInfo && handlerInfo.path && !String(handlerInfo.path).startsWith('/api/protocol/list');
        })
      ]
    }
  }
};

export const LoadingComparison: Story = {
  name: "Loading Comparison Data",
  parameters: {
    msw: {
      handlers: [
        // Use default /api/protocol/list handler from mockApiHandlers
        ...mockApiHandlers.filter(handler => {
            const handlerInfo = (handler as any).info;
            return handlerInfo && handlerInfo.path && !String(handlerInfo.path).startsWith('/api/protocol/compare');
        }),
        http.post('/api/protocol/compare', () => {
           // Simulate a long delay
           return new Promise(resolve => setTimeout(() => resolve(HttpResponse.json({})), 300000));
        })
      ]
    }
  },
  // To see this state, you'd typically interact with the DefaultView by selecting items.
  // Or, modify ProtocolComparatorPage to accept initialSelectedIds for story purposes.
  // This story primarily ensures the /api/protocol/compare mock is delayed.
  // The user would select items in Storybook, and then this delayed mock would be hit.
};

export const ErrorComparison: Story = {
  name: "Error Fetching Comparison Data",
  parameters: {
    msw: {
      handlers: [
        ...mockApiHandlers.filter(handler => {
            const handlerInfo = (handler as any).info;
            return handlerInfo && handlerInfo.path && !String(handlerInfo.path).startsWith('/api/protocol/compare');
        }),
        http.post('/api/protocol/compare', () => {
          return HttpResponse.json({ message: 'Simulated server error fetching comparison' }, { status: 500 });
        })
      ]
    }
  }
};

export const WithSortingAndFiltering: Story = {
  name: "Default with Sorting & Filtering",
  // This story will use the default mock handlers from `mockApiHandlers`
  // defined at the meta level. Interactions for sorting/filtering are manual in Storybook.
};
