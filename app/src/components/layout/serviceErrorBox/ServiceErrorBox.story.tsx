import type { Meta, StoryObj } from '@storybook/react';
import Component from './ServiceErrorBox';

const meta = {
    title: 'Layout/ServiceErrorBox',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const ServiceErrorBox: Story = {
    args: {
        message: 'This is an example service error message',
    },
};
export default meta;
