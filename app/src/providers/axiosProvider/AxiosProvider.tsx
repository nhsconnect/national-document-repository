import axios, { AxiosInstance } from 'axios';
import React, { createContext, useContext, useEffect, ReactNode, useRef } from 'react';
import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import getAuthRefresh from '../../helpers/requests/getAuthRefresh';

type AxiosContextType = AxiosInstance | null;

const AxiosContext = createContext<AxiosContextType>(null);

const AxiosProvider = ({ children }: { children: ReactNode }) => {
    const [session, setSession] = useSessionContext();
    const baseUrl = useBaseAPIUrl();
    const axiosInstanceRef = useRef<AxiosInstance | null>(null);

    useEffect(() => {
        if (session.auth && !axiosInstanceRef.current) {
            const instance = axios.create({
                baseURL: baseUrl,
            });

            instance.interceptors.request.use(
                (config) => {
                    const token = session.auth?.authorisation_token;
                    if (token) {
                        config.headers['Content-Type'] = 'application/json';
                        config.headers['Authorization'] = token;
                    }
                    return config;
                },
                (error) => Promise.reject(error),
            );

            // Response interceptor to handle token refresh on 403
            instance.interceptors.response.use(
                (response) => response,
                async (error) => {
                    const originalRequest = error.config;
                    if (error.response?.status === 403 && !originalRequest._retry) {
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

            axiosInstanceRef.current = instance;
        }
    }, [baseUrl, session, setSession]);

    return (
        <AxiosContext.Provider value={axiosInstanceRef.current}>{children}</AxiosContext.Provider>
    );
};

export default AxiosProvider;

export const useAxios = () => useContext(AxiosContext) as AxiosInstance;
