import React from 'react';
import { USER_ROLE } from '../../types/generic/roles';
import { buildPatientDetails } from '../../helpers/test/testBuilders';

type Props = {
  role: USER_ROLE;
};

function PatientResultPage({ role }: Props) {
  const patient = buildPatientDetails();
  return <div>{role}</div>;
}

export default PatientResultPage;
