import type { Meta, StoryObj } from '@storybook/react';
import Component from './FeedbackPage';

const meta = {
    title: 'Pages/FeedbackPage',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const FeedbackPage: Story = {
    args: {},
};
export default meta;
