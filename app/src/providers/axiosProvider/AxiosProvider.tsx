import axios, { AxiosInstance } from 'axios';
import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import getAuthRefresh from '../../helpers/requests/getAuthRefresh';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';

type AxiosContextType = AxiosInstance | null;

const AxiosContext = createContext<AxiosContextType>(null);

export const AxiosProvider = ({ children }: { children: ReactNode }) => {
    const [axiosInstance, setAxiosInstance] = useState<AxiosInstance | null>(null);
    const [session, setSession] = useSessionContext();
    const baseUrl = useBaseAPIUrl();
    const baseApiHeaders = useBaseAPIHeaders();
    useEffect(() => {
        if (session.auth) {
            const instance = axios.create({
                baseURL: baseUrl,
                headers: baseApiHeaders,
            });

            instance.interceptors.response.use(
                (response) => response,
                async (error) => {
                    const originalRequest = error.config;
                    if (error.response.status === 403 && !originalRequest._retry) {
                        originalRequest._retry = true;
                        const auth = await getAuthRefresh({
                            axios: instance,
                            refreshToken: session.auth?.refresh_token ?? '',
                        });
                        if (auth.authorisation_token) {
                            setSession({
                                ...session,
                                auth,
                            });
                            originalRequest.headers['Authorization'] = auth.authorisation_token;
                            return instance(originalRequest);
                        }
                    }
                    return Promise.reject(error);
                },
            );

            setAxiosInstance(instance);
        }
    }, [baseApiHeaders, baseUrl, session, setSession]);

    return <AxiosContext.Provider value={axiosInstance}>{children}</AxiosContext.Provider>;
};

// Custom hook to use the Axios instance
export const useAxios = () => {
    const context = useContext(AxiosContext);
    if (!context) {
        throw new Error('useAxios must be used within an AxiosProvider');
    }
    return context;
};
