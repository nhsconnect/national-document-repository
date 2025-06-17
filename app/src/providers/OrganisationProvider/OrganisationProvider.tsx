import { createContext, useContext, useState } from 'react';
import type { ReactNode, Dispatch, SetStateAction } from 'react';
import { PatientDetails } from '../../types/generic/patientDetails';
import { OrganisationDetails } from '../../types/generic/organisationDetails';

type Props = {
    organisationDetails?: OrganisationDetails[] | null;
    children: ReactNode;
};

export type OrganisationContext = [
    OrganisationDetails[] | null,
    Dispatch<SetStateAction<OrganisationDetails[] | null>>,
];

const OrganisationDetailsContext = createContext<OrganisationContext | null>(null);

const OrganisationDetailsProvider = ({ children, organisationDetails }: Props) => {
    const organisationState: OrganisationContext = useState<OrganisationDetails[] | null>(
        organisationDetails ?? null,
    );

    return (
        <OrganisationDetailsContext.Provider value={organisationState}>
            {children}
        </OrganisationDetailsContext.Provider>
    );
};

export default OrganisationDetailsProvider;
export const useOrganisationDetailsContext = () =>
    useContext(OrganisationDetailsContext) as OrganisationContext;
