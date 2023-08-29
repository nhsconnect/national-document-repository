import type { Meta, StoryObj } from '@storybook/react';
import SpinnerButton from './SpinnerButton';

const meta = {
  title: 'Generic/SpinnerButton',
  component: SpinnerButton,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen'
  }
} satisfies Meta<typeof SpinnerButton>;

type Story = StoryObj<typeof meta>;

export const LoggedIn: Story = {
  args: {
    status: 'Loading...',
    disabled: false
  }
};
export default meta;
