import type { Meta, StoryObj } from '@storybook/react';
import Component from './PatientResultPage';
import { USER_ROLE } from '../../types/generic/roles';

const meta = {
    title: 'Pages/PatientResultPage',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const PatientResultPage: Story = {
    args: {
        role: USER_ROLE.PCSE,
    },
};
export default meta;
