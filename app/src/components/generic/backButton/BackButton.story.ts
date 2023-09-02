import type { Meta, StoryObj } from '@storybook/react';
import Component from './BackButton';

const meta = {
    title: 'Generic/BackButton',
    component: Component,
    // This component will have an automatically generated Autodocs entry: https://storybook.js.org/docs/react/writing-docs/autodocs
    tags: ['autodocs'],
    parameters: {
        // More on how to position stories at: https://storybook.js.org/docs/react/configure/story-layout
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const BackButton: Story = {
    args: {},
};

export default meta;
