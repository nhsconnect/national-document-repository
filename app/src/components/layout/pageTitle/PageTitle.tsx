import { useEffect } from 'react';

type Props = {
    pageTitle: string;
};

const PageTitle = ({ pageTitle }: Props) => {
    const serviceName = 'NHS Patient Record Migration Service';
    useEffect(() => {
        document.title = pageTitle + ' - ' + serviceName;
    }, [pageTitle]);
};

export default PageTitle;
