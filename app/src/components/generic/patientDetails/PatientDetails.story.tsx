import type { Meta, StoryObj } from '@storybook/react';
import Component from './PatientDetails';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';

const meta = {
    title: 'Blocks/PatientDetails',
    component: Component,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const PatientDetails: Story = {
    args: {
        patientDetails: buildPatientDetails(),
    },
};
export default meta;
