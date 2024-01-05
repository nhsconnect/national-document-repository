import type { Meta, StoryObj } from '@storybook/react';
import Component from './WarningText';

const meta = {
    title: 'Blocks/WarningText',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const OrgSelectPage: Story = {
    args: {
        text: 'Some warning text',
        iconFallbackText: 'warning',
    },
};
export default meta;
