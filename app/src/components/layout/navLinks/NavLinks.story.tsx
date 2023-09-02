import type { Meta, StoryObj } from '@storybook/react';
import Component from './NavLinks';

const meta = {
    title: 'Layout/NavLinks',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const NavLinks: Story = {
    args: {},
};
export default meta;
