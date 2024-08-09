import { useEffect } from 'react';

type Props = {
    pageTitle: string;
};

function useTitle({ pageTitle }: Props) {
    const serviceName = 'Access and store digital patient documents';
    useEffect(() => {
        document.title = pageTitle + ' - ' + serviceName;
    }, [pageTitle]);
}

export default useTitle;
