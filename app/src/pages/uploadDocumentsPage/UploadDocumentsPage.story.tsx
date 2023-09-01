import type { Meta, StoryObj } from '@storybook/react';
import Component from './UploadDocumentsPage';

const meta = {
    title: 'Pages/UploadDocumentsPage',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const UploadDocumentsPage: Story = {
    args: {},
};
export default meta;
