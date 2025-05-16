/// <reference types="vite/client" />
/// <reference types="vite-plugin-svgr/client" />
/// <reference types="vite/types/importMeta.d.ts" />
/// <reference types="vitest/globals" />

declare module '*.svg' {
    import React = require('react');
    export const ReactComponent: React.FC<React.SVGProps<SVGSVGElement>>;
    const src: string;
    export default src;
}

interface ImportMetaEnv {
    readonly VITE_MONITOR_ACCOUNT_ID: string;
    VITE_ENVIRONMENT: string;
    readonly VITE_RUM_IDENTITY_POOL_ID: string;
    readonly VITE_AWS_REGION: string;
    readonly VITE_DOC_STORE_API_ENDPOINT: string;
    readonly VITE_IMAGE_VERSION: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}
