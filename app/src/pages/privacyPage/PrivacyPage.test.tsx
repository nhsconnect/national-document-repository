import { LinkProps } from 'react-router-dom';
import useRole from '../../helpers/hooks/useRole';
import { act, render, screen, waitFor } from '@testing-library/react';
import PrivacyPage from './PrivacyPage';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import userEvent from '@testing-library/user-event';
import { routes } from '../../types/generic/routes';
import { runAxeTest } from '../../helpers/test/axeTestHelper';

const mockedUseNavigate = jest.fn();
jest.mock('../../helpers/hooks/useRole');
const mockedUseRole = useRole as jest.Mock;
jest.mock('react-router-dom', () => ({
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockedUseNavigate,
}));

describe('PrivacyPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUseRole.mockReturnValue(null);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders page headers', () => {
            render(<PrivacyPage />);

            const contentHeaders = [
                'Privacy notice',
                'What happens with my personal information?',
                'Feedback form privacy notice',
                'Our permission to process and store patient data',
                'Further information',
                'Contact us',
            ];
            contentHeaders.forEach((str) => {
                expect(screen.getByRole('heading', { name: str })).toBeInTheDocument();
            });
        });

        it('renders legal privacy content', () => {
            render(<PrivacyPage />);

            const contents = [
                /If you use the 'Access and store digital patient documents' service using your/i,
                /credentials, your NHS Care Identity credentials are managed by NHS England/i,
                /This means NHS England is the data controller for any personal information/i,
                /that you provided to get NHS Care Identity credentials/i,
                /NHS England uses this information only to verify your identity/i,
                /When verifying your identity, our role is a "processor"/i,
                /We must act under instructions provided by NHS England \(the "controller"\)/i,
                /To find out more about NHS England's Privacy Notice/i,
                /and its Terms and Conditions, view the/i,
                /This only applies to information you provide through NHS England/i,
                /When submitting your details using our/i,
                /any personal information you give to us will be processed in accordance with the/i,
                /We use the information you submitted to process your request and provide/i,
                /relevant information or services you have requested/i,
                /This will help support us in developing this service/i,
            ];
            contents.forEach((str) => {
                expect(screen.getByText(str)).toBeInTheDocument();
            });
        });

        it('renders our permission to process and store patient data content', () => {
            render(<PrivacyPage />);

            const contents = [
                /This service has legal permission to process and store patient data through the/i,
                /The National Data Processing Deed enables NHS England to:/i,
                /act as the data processor for all GP practices in England/i,
                /store the digitised Lloyd George records of patients registered at these GP practices/i,
                /This deed operates under the/i,
                /GP practices in England are automatically signed up to /i,
                /the National Data Processing Deed, so you don't need to do anything./i,
                /NHS England's role as a data controller/i,
                /If you have any questions about the National Data Processing Deed,/i,
                /or our privacy policy, you can contact the team on/i,
            ];
            contents.forEach((str) => {
                expect(screen.getByText(str)).toBeInTheDocument();
            });
        });

        it('renders public clickable links', () => {
            render(<PrivacyPage />);
            expect(screen.getByTestId('cis2-link')).toHaveAttribute(
                'href',
                'https://am.nhsidentity.spineservices.nhs.uk/openam/XUI/?realm=/#/',
            );
            expect(screen.getByTestId('cis2-service-link')).toHaveAttribute(
                'href',
                'https://digital.nhs.uk/services/care-identity-service',
            );
            expect(screen.getByTestId('gdpr-link')).toHaveAttribute(
                'href',
                'https://digital.nhs.uk/data-and-information/keeping-data-safe-and-benefitting-the-public/gdpr#:~:text=The%20GDPR%20came%20into%20effect,in%20line%20with%20the%20regulations',
            );
            expect(screen.getByTestId('permission-section-gdpr-link')).toHaveAttribute(
                'href',
                'https://digital.nhs.uk/data-and-information/keeping-data-safe-and-benefitting-the-public/gdpr#:~:text=The%20GDPR%20came%20into%20effect,in%20line%20with%20the%20regulations',
            );
            expect(screen.getByTestId('data-controller-link')).toHaveAttribute(
                'href',
                'https://www.england.nhs.uk/contact-us/privacy-notice/nhs-england-as-a-data-controller/',
            );
        });

        it('does not render a clickable link for feedback form if user logged out', () => {
            mockedUseRole.mockReturnValue(null);
            render(<PrivacyPage />);
            expect(screen.queryByTestId('feedback-link')).not.toHaveAttribute('href');
            expect(screen.queryByTestId('feedback-link')).not.toHaveAttribute('to');
        });

        it('renders a clickable link for feedback form if user logged in', () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            render(<PrivacyPage />);
            expect(screen.queryByTestId('feedback-link')).not.toHaveAttribute('href');
            expect(screen.getByTestId('feedback-link')).toHaveAttribute('to', '#');
        });

        it('pass accessibility checks', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            render(<PrivacyPage />);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        describe('Navigation', () => {
            it('navigates to feedback form when link is clicked and user is logged in', async () => {
                mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
                render(<PrivacyPage />);
                expect(screen.queryByTestId('feedback-link')).not.toHaveAttribute('href');
                expect(screen.getByTestId('feedback-link')).toHaveAttribute('to', '#');
                act(() => {
                    userEvent.click(
                        screen.getByRole('link', {
                            name: 'feedback form',
                        }),
                    );
                });
                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(routes.FEEDBACK);
                });
            });
        });
    });
});
