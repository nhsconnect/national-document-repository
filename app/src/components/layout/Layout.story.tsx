import type { Meta, StoryObj } from '@storybook/react';
import Component from './Layout';

const meta = {
    title: 'Layout/Layout',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const Layout: Story = {
    args: {
        children: <div />,
    },
};
export default meta;
