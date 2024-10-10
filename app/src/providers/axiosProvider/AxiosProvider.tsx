import axios, { AxiosInstance } from 'axios';
import React, { createContext, useContext, ReactNode, useMemo } from 'react';
import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import getAuthRefresh from '../../helpers/requests/getAuthRefresh';

type AxiosContextType = AxiosInstance | null;

const AxiosContext = createContext<AxiosContextType>(null);

const AxiosProvider = ({ children }: { children: ReactNode }) => {
    const [session, setSession] = useSessionContext();
    const baseUrl = useBaseAPIUrl();

    const axiosInstance = useMemo(() => {
        const instance = axios.create({
            baseURL: baseUrl,
            headers: {
                'Content-Type': 'application/json',
                Authorization: session.auth?.authorisation_token,
            },
        });

        instance.interceptors.response.use(
            (response) => response,
            async (error) => {
                const originalRequest = error.config;
                if (error.response?.status === 403 && !originalRequest._retry) {
                    originalRequest._retry = true;
                    try {
                        const auth = await getAuthRefresh({
                            axios: instance,
                            refreshToken: session.auth?.refresh_token ?? '',
                        });

                        if (auth?.authorisation_token) {
                            setSession({
                                ...session,
                                auth,
                            });
                            originalRequest.headers['Authorization'] = auth.authorisation_token;
                            return instance(originalRequest);
                        }
                    } catch (refreshError) {
                        return Promise.reject(refreshError);
                    }
                }
                return Promise.reject(error);
            },
        );

        return instance;
    }, [session, baseUrl, setSession]);

    return <AxiosContext.Provider value={axiosInstance}>{children}</AxiosContext.Provider>;
};

export const useAxios = () => {
    const context = useContext(AxiosContext);
    if (!context) {
        throw new Error('useAxios must be used within an AxiosProvider');
    }
    return context;
};
export default AxiosProvider;
