import { useConfigContext } from '../../providers/configProvider/ConfigProvider';

function useConfig() {
    const [config] = useConfigContext();
    return config;
}

export default useConfig;
