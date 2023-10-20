import type { Meta, StoryObj } from '@storybook/react';
import Component from './Spinner';

const meta = {
    title: 'Blocks/Spinner',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const OrgSelectPage: Story = {
    args: {
        status: 'Spinner text...',
    },
};
export default meta;
