import type { Meta } from '@storybook/react';
import Component from './DocumentSearchResultsPage';

const meta = {
    title: 'Pages/DocumentSearchResultsPage',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

export default meta;
