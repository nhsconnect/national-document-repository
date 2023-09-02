import type { Meta, StoryObj } from '@storybook/react';
import RoleSelectPage from './RoleSelectPage';

const meta = {
    title: 'Pages/OrgSelectPage',
    component: RoleSelectPage,
    tags: ['autodocs'],
    parameters: {
        layout: 'fullscreen',
    },
} satisfies Meta<typeof RoleSelectPage>;

type Story = StoryObj<typeof meta>;

export const OrgSelectPage: Story = {
    args: {},
};
export default meta;
