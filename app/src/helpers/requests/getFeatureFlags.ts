import { AxiosInstance } from 'axios';
import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';

import { defaultFeatureFlags, FeatureFlags } from '../../types/generic/featureFlags';

type Args = {
    baseHeaders: AuthHeaders;
    axios: AxiosInstance;
};

type GetFeatureFlagsResponse = {
    data: FeatureFlags;
};

const getFeatureFlags = async ({ axios, baseHeaders }: Args) => {
    try {
        const { data }: GetFeatureFlagsResponse = await axios.get(endpoints.FEATURE_FLAGS, {
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
