import type { Meta, StoryObj } from '@storybook/react';
import Component from './PatientSimpleSummary';

const meta = {
    title: 'Blocks/PatientSimpleSummary',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const PatientSummary: Story = {
    args: {},
};
export default meta;
