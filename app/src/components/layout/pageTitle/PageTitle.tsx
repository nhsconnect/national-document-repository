import { useEffect } from 'react';

type Props = {
    pageTitle: string;
};

const PageTitle = ({ pageTitle }: Props) => {
    const serviceName = 'Digital Lloyd George records';
    useEffect(() => {
        document.title = pageTitle + ' - ' + serviceName;
    }, [pageTitle]);
};

export default PageTitle;
