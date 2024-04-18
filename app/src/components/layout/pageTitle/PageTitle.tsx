import { useEffect } from 'react';

type Props = {
    pageTitle: string;
};

function PageTitle({ pageTitle }: Props) {
    const serviceName = 'Digital Lloyd George records';
    useEffect(() => {
        console.log(document.title);
        document.title = pageTitle + ' - ' + serviceName;
    }, [pageTitle]);
}

export default PageTitle;
