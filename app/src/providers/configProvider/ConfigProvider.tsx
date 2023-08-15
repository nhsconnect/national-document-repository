import { createContext, useContext } from "react";

const ConfigContext = createContext(null);

export const useBaseAPIUrl = (apiName: string) => {
  const config = useContext(ConfigContext);
  // @ts-ignore
  const apiEndpoints = config?.API.endpoints;

  if (apiEndpoints === undefined) {
    throw Error(`Endpoint for ${apiName} is not configured`);
  }

  const endpointConfiguration = apiEndpoints.find(
    (endpoint: any) => endpoint.name === apiName
  );

  if (endpointConfiguration === undefined) {
    throw Error(`Endpoint for ${apiName} is not configured`);
  }

  return endpointConfiguration.endpoint;
};

// @ts-ignore
const ConfigProvider = ({ children, config }) => {
  return (
    <ConfigContext.Provider value={config}>{children}</ConfigContext.Provider>
  );
};

export default ConfigProvider;
