import type { Meta, StoryObj } from '@storybook/react';
import Component from './ErrorBox';

const meta = {
    title: 'Generic/ErrorBox',
    component: Component,
    // This component will have an automatically generated Autodocs entry: https://storybook.js.org/docs/react/writing-docs/autodocs
    tags: ['autodocs'],
    parameters: {
        // More on how to position stories at: https://storybook.js.org/docs/react/configure/story-layout
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const ErrorBox: Story = {
    args: {
        errorBoxSummaryId: '0',
        messageTitle: 'This is an example error',
        messageBody: 'Use this field to explain the error further',
    },
};

export const ErrorLinkBox: Story = {
    args: {
        errorBoxSummaryId: '1',
        messageTitle: 'This is an example linked error',
        messageLinkBody:
            'Use this field to explain the error further and where the link will take you to',
        errorInputLink: '/',
    },
};

export default meta;
