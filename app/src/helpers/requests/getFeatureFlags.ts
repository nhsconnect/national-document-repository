import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';

import axios from 'axios';
import { FeatureFlags } from '../../types/generic/featureFlags';

type Args = {
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

type GetFeatureFlagsResponse = {
    data: FeatureFlags;
};

export const defaultFeatureFlags = {
    testFeature1: false,
    testFeature2: false,
    testFeature3: false,
};

const getFeatureFlags = async ({ baseUrl, baseHeaders }: Args) => {
    const gatewayUrl = baseUrl + endpoints.FEATURE_FLAGS;
    try {
        const { data }: GetFeatureFlagsResponse = await axios.get(gatewayUrl, {
            headers: {
                ...baseHeaders,
            },
        });
        return data;
    } catch (e) {
        return defaultFeatureFlags;
    }
};

export default getFeatureFlags;
