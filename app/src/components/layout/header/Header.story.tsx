import type { Meta, StoryObj } from '@storybook/react';
import Component from './Header';

const meta = {
    title: 'Layout/Header',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const Header: Story = {
    args: {},
};
export default meta;
