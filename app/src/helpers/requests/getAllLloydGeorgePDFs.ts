import { AxiosError } from 'axios';

const getAllLloydGeorgePDFs = async () => {
    try {
        const response = await Promise.resolve(true);
    } catch (e) {
        const error = e as AxiosError;
        throw error;
    }
};

export default getAllLloydGeorgePDFs;
