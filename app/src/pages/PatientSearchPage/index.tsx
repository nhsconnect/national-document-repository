import React from 'react';
import { routes } from '../../types/blocks/routes';

type Props = {
  route: routes;
};

function PatientSearchPage({ route }: Props) {
  const handleSearch = () => {
    // GP Role
    if (route === routes.DOWNLOAD_SEARCH) {
      // Make PDS patient search request
    }

    // PCSE Role
    else if (route === routes.UPLOAD_SEARCH) {
      // Make PDS and Dynamo document store search request
    }
  };

  return <div>PatientSearchPage</div>;
}

export default PatientSearchPage;
