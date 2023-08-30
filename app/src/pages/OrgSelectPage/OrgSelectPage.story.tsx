import type { Meta, StoryObj } from '@storybook/react';
import Component from './OrgSelectPage';

const meta = {
  title: 'Pages/OrgSelectPage',
  component: Component,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen'
  }
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const OrgSelectPage: Story = {
  args: {}
};
export default meta;
