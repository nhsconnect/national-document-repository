import { useEffect } from 'react';

type Props = {
    pageTitle: string;
};

function useTitle({ pageTitle }: Props) {
    const serviceName = 'Digital Lloyd George records';
    useEffect(() => {
        document.title = pageTitle + ' - ' + serviceName;
    }, [pageTitle]);
}

export default useTitle;
