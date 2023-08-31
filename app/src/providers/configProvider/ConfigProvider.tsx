import { createContext } from "react";

const ConfigContext = createContext(null);

export const useBaseAPIUrl = () => {
  const apiEndpoint: string | undefined = process.env.REACT_APP_DOC_STORE_API_ENDPOINT;

  if (!apiEndpoint) {
    throw Error(`API endpoint is not configured`);
  }

  return apiEndpoint;
};

// @ts-ignore
const ConfigProvider = ({ children, config }) => {
  return (
    <ConfigContext.Provider value={config}>{children}</ConfigContext.Provider>
  );
};

export default ConfigProvider;
