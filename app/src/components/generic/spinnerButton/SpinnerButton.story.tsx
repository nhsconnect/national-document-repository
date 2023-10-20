import type { Meta, StoryObj } from '@storybook/react';
import Component from './SpinnerButton';

const meta = {
    title: 'Blocks/SpinnerButton',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const OrgSelectPage: Story = {
    args: {
        id: 'spinner-button',
        status: 'Loading...',
        disabled: false,
    },
};
export default meta;
