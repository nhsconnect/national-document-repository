import type { Meta, StoryObj } from '@storybook/react';
import Component from './StartPage';

const meta = {
    title: 'Pages/HomePage',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const HomePage: Story = {
    args: {},
};
export default meta;
