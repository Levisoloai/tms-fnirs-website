import type { Meta, StoryObj } from '@storybook/react';
import React, { useState } from 'react';
import Modal from './Modal';
import Button from './Button'; // Assuming Button component exists for triggering

const meta: Meta<typeof Modal> = {
  title: 'UI/Modal',
  component: Modal,
  tags: ['autodocs'],
  argTypes: {
    isOpen: { control: 'boolean', description: 'Controls if the modal is open or closed. Note: For the "Default" story, use the "Open Modal" button instead of this control.' },
    title: { control: 'text' },
    onClose: { action: 'closed', description: 'Callback when the modal is requested to close (e.g., by Esc key, overlay click, or close button).' },
    children: { control: 'object' }, // Or 'text' for simple strings
  },
};
export default meta;

type Story = StoryObj<typeof Modal>;

// Story that manages its own state to show/hide the modal
export const Default: Story = {
  args: {
    // isOpen: false, // Initial state handled by render function
    title: 'Sample Modal Title',
    children: <p>This is the content of the modal. You can put anything here, like text, forms, or other components. Try pressing the Escape key or clicking the overlay to close.</p>,
  },
  render: function Render(args) {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [isOpen, setIsOpen] = useState(args.isOpen || false);
    const handleOpen = () => setIsOpen(true);
    const handleClose = () => {
      setIsOpen(false);
      args.onClose?.(); // Call original onClose if provided by Storybook action
    };

    return (
      <>
        <p className="text-gray-300 mb-4">Click the button below to open the modal. The `isOpen` arg in Storybook controls will not directly control this story; use the button.</p>
        <Button onClick={handleOpen}>Open Modal</Button>
        <Modal {...args} isOpen={isOpen} onClose={handleClose} />
      </>
    );
  },
};

export const PreOpenedModal: Story = {
    args: {
        isOpen: true,
        title: 'Already Open Modal',
        children: <p>This modal is open by default based on its `isOpen` arg. You can close it by pressing Escape, clicking the overlay, or the close button. Storybook's `isOpen` control can also be used to toggle it.</p>
    }
    // No custom render needed if we just want to show it open via args,
    // but we must ensure the onClose action from Storybook is wired up if we want to see it in the actions panel.
    // For direct control via args AND seeing actions, a more complex render is needed.
    // However, for just showing it pre-opened, this is fine.
    // To make it interactive with Storybook's controls properly, its render function would need to handle args.isOpen.
    // Let's make it properly interactive with Storybook controls:
    ,render: function RenderPreOpened(args) {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const [isOpen, setIsOpen] = useState(args.isOpen || true); // Default to true for pre-opened

        // Effect to sync with Storybook control for isOpen
        // eslint-disable-next-line react-hooks/rules-of-hooks
        React.useEffect(() => {
            setIsOpen(args.isOpen || false);
        }, [args.isOpen]);
        
        const handleClose = () => {
          setIsOpen(false);
          args.onClose?.(); 
        };

        return (
          <>
            <p className="text-gray-300 mb-4">This modal's `isOpen` state is directly tied to the Storybook control.</p>
            <Modal {...args} isOpen={isOpen} onClose={handleClose} />
          </>
        );
    }
};

export const LongContentModal: Story = {
  args: {
    title: 'Modal with Long Content',
    children: (
      <div className="space-y-4">
        <p>This modal contains a lot of text to demonstrate scrolling behavior within the modal body if it were implemented (note: current Modal component does not have explicit scrolling for children, content will overflow or be cut based on browser behavior and parent height).</p>
        {[...Array(15)].map((_, i) => (
          <p key={i}>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
        ))}
      </div>
    ),
  },
  render: function RenderLongContent(args) {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [isOpen, setIsOpen] = useState(args.isOpen || false);
    const handleOpen = () => setIsOpen(true);
    const handleClose = () => {
      setIsOpen(false);
      args.onClose?.();
    };

    return (
      <>
        <Button onClick={handleOpen}>Open Long Content Modal</Button>
        <Modal {...args} isOpen={isOpen} onClose={handleClose} />
      </>
    );
  },
};
