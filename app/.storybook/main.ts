import type { StorybookConfig } from '@storybook/react-webpack5';

const config: StorybookConfig = {
    stories: [
        '../src/components/**/*.story.@(js|jsx|mjs|ts|tsx)',
        '../src/pages/**/*.story.@(js|jsx|mjs|ts|tsx)',
    ],
    addons: [
        '@storybook/addon-links',
        '@storybook/addon-essentials',
        '@storybook/preset-create-react-app',
        '@storybook/addon-onboarding',
        '@storybook/addon-interactions',
        {
            name: '@storybook/addon-styling',
            options: {},
        },
    ],
    framework: {
        name: '@storybook/react-webpack5',
        options: {},
    },
    docs: {
        autodocs: 'tag',
    },
    staticDirs: ['../public'],
};
export default config;
