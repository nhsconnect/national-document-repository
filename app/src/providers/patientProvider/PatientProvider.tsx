import { createContext, useContext, useState } from 'react';
import type { ReactNode, Dispatch, SetStateAction } from 'react';
import { Patient } from '../../types/generic/patient';

type Props = {
  patient?: Patient | null;
  children: ReactNode;
};

export type PatientContext = [
  Patient | null,
  Dispatch<SetStateAction<Patient | null>>
];

const PatientDetailsContext = createContext<PatientContext | null>(null);

const PatientDetailsProvider = ({ children, patient }: Props) => {
  const patientState: PatientContext = useState(patient ?? null);

  return (
    <PatientDetailsContext.Provider value={patientState}>
      {children}
    </PatientDetailsContext.Provider>
  );
};

export default PatientDetailsProvider;
export const usePatientDetailsContext = () => useContext(PatientDetailsContext);
