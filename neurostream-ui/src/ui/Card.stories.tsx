import type { Meta, StoryObj } from '@storybook/react';
import Card from './Card';

const meta: Meta<typeof Card> = {
  title: 'UI/Card',
  component: Card,
  tags: ['autodocs'],
  argTypes: {
    title: { control: 'text' },
    abstract: { control: 'text' },
    // links: { control: 'object' }, // Storybook can struggle with complex objects in controls
    // tags: { control: 'object' },  // Can use 'array' but 'object' is often better for [{...}]
    children: { control: 'text' }, // For simple text children, or disable if only ReactNode
  },
};
export default meta;

type Story = StoryObj<typeof Card>;

export const Default: Story = {
  args: {
    title: 'Comprehensive Card Example',
    abstract: 'This card demonstrates all features: a title, an abstract, multiple links, and several tags. It is designed to showcase the full capabilities of the Card component.',
    links: [
      { href: '#link1', text: 'Primary Link' },
      { href: '#link2', text: 'Secondary Link' },
      { href: '#link3', text: 'Another Link' },
    ],
    tags: ['Neuroscience', 'AI Research', 'Data Visualization', 'Open Science'],
  },
};

export const WithCustomChildren: Story = {
  args: {
    title: 'Card with Custom Content',
    children: <div className="bg-gray-700 p-4 rounded-md"><p className="text-white font-bold">This is a custom ReactNode child.</p><p className="text-gray-300 mt-2">It replaces the abstract and demonstrates the flexibility of the `children` prop.</p></div>,
    links: [
      { href: '#custom', text: 'Custom Link' }
    ],
    tags: ['Custom Content', 'ReactNode', 'Flexibility'],
  },
};

export const Minimal: Story = {
  args: {
    title: 'Minimal Card Configuration',
    abstract: 'This card only has a title and a short abstract. No links or tags are provided to demonstrate a simpler use case.',
  },
};

export const WithLinksAndTagsNoAbstract: Story = {
  args: {
    title: 'Links & Tags, No Abstract',
    links: [
      { href: '#datasheet', text: 'Datasheet' },
      { href: '#sourcecode', text: 'Source Code' },
    ],
    tags: ['Technical', 'Documentation'],
  }
};

export const TitleOnly: Story = {
  args: {
    title: 'Title Only Card',
  }
};
