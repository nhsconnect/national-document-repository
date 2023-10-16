import { render, screen, waitFor } from '@testing-library/react';
import LloydGeorgeRecordPage from './LloydGeorgeRecordPage';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import {
    buildPatientDetails,
    buildLgSearchResult,
    buildUserAuth,
} from '../../helpers/test/testBuilders';
import { getFormattedDate } from '../../helpers/utils/formatDate';
import axios from 'axios';
import SessionProvider, { Session } from '../../providers/sessionProvider/SessionProvider';

jest.mock('axios');
jest.mock('react-router');

const mockAxios = axios as jest.Mocked<typeof axios>;
const mockPatientDetails = buildPatientDetails();

describe('LloydGeorgeRecordPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders patient details', async () => {
        const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
        const dob = getFormattedDate(new Date(mockPatientDetails.birthDate));
        mockAxios.get.mockReturnValue(Promise.resolve({ data: buildLgSearchResult() }));

        renderPage();

        await waitFor(async () => {
            expect(screen.getByText(patientName)).toBeInTheDocument();
        });
        expect(screen.getByText(`Date of birth: ${dob}`)).toBeInTheDocument();
        expect(screen.getByText(/NHS number/)).toBeInTheDocument();
    });

    it('renders initial lg record view', async () => {
        renderPage();
        await waitFor(async () => {
            expect(screen.getByText('Lloyd George record')).toBeInTheDocument();
        });
    });

    it('renders initial lg record view with no docs available text if there is no LG record', async () => {
        const errorResponse = {
            response: {
                status: 404,
                message: '404 no docs found',
            },
        };

        mockAxios.get.mockImplementation(() => Promise.reject(errorResponse));

        renderPage();

        await waitFor(async () => {
            expect(screen.getByText('No documents are available')).toBeInTheDocument();
        });

        expect(screen.queryByText('View record')).not.toBeInTheDocument();
    });

    it('displays Loading... until the pdf is fetched', async () => {
        mockAxios.get.mockReturnValue(Promise.resolve({ data: buildLgSearchResult() }));

        renderPage();

        await waitFor(async () => {
            expect(screen.getByText('Loading...')).toBeInTheDocument();
        });
    });

    it('renders initial lg record view with file info when LG record is returned by search', async () => {
        mockAxios.get.mockReturnValue(Promise.resolve({ data: buildLgSearchResult() }));

        renderPage();

        await waitFor(() => {
            expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
        });
        expect(screen.getByText('View record')).toBeInTheDocument();
        expect(screen.getByText('View in full screen')).toBeInTheDocument();

        expect(screen.getByText('Lloyd George record')).toBeInTheDocument();
        expect(screen.queryByText('No documents are available')).not.toBeInTheDocument();
        expect(
            screen.getByText('7 files | File size: 7 bytes | File format: PDF'),
        ).toBeInTheDocument();
    });
});

const renderPage = () => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: true,
    };
    render(
        <SessionProvider sessionOverride={auth}>
            <PatientDetailsProvider patientDetails={mockPatientDetails}>
                <LloydGeorgeRecordPage />
            </PatientDetailsProvider>
        </SessionProvider>,
    );
};
