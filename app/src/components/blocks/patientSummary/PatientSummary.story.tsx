import type { Meta, StoryObj } from '@storybook/react';
import Component from './PatientSummary';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';

const meta = {
  title: 'PatientResultPage/PatientSummary',
  component: Component,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen'
  }
} satisfies Meta<typeof Component>;

type Story = StoryObj<typeof meta>;

export const PatientSummary: Story = {
  args: {
    patientDetails: buildPatientDetails()
  }
};
export default meta;
