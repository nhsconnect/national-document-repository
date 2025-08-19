import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import { SATISFACTION_CHOICES } from '../../types/pages/feedbackPage/types';
import FeedbackPage from './FeedbackPage';
import { fillInForm } from '../../helpers/test/formUtils';
import { routes } from '../../types/generic/routes';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import { afterEach, beforeEach, describe, expect, it, vi, Mock, Mocked } from 'vitest';

vi.mock('axios');
vi.mock('../../helpers/hooks/useBaseAPIUrl');
vi.mock('../../helpers/hooks/useBaseAPIHeaders');
const mockedUseNavigate = vi.fn();
const mockedAxios = axios as Mocked<typeof axios>;
const mockedBaseURL = useBaseAPIUrl as Mock;
const baseURL = 'http://test';
Date.now = () => new Date('2020-01-01T00:00:00.000Z').getTime();

vi.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));

const clickSubmitButton = async () => {
    await userEvent.click(screen.getByRole('button', { name: 'Send feedback' }));
};

const renderComponent = () => {
    return render(<FeedbackPage />);
};

describe('<FeedbackPage />', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        mockedBaseURL.mockReturnValue(baseURL);
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('renders page content', () => {
        renderComponent();

        expect(screen.getByTestId('feedback-page-header')).toBeInTheDocument();
        expect(screen.getByTestId('feedback-text-section')).toBeInTheDocument();
        expect(screen.getByTestId('feedback-radio-section')).toBeInTheDocument();
        expect(screen.getByTestId('feedback-details-section')).toBeInTheDocument();
    });

    describe('Accessibility', () => {
        it('pass accessibility checks at page entry point', async () => {
            render(<FeedbackPage />);
            const results = await runAxeTest(document.body);

            expect(results).toHaveNoViolations();
        });
    });

    it('renders a primary button for submit', () => {
        renderComponent();

        expect(screen.getByTestId('submit-feedback')).toBeInTheDocument();
    });

    describe('User interactions', () => {
        it('on submit, call sendEmail() with the data that user had filled in', async () => {
            mockedAxios.post.mockImplementation(() =>
                Promise.resolve({ status: 200, data: 'Success' }),
            );

            const mockInputData = {
                feedbackContent: 'Mock feedback content',
                howSatisfied: SATISFACTION_CHOICES.VerySatisfied,
                respondentName: 'Jane Smith',
                respondentEmail: 'jane_smith@testing.com',
            };

            renderComponent();

            await fillInForm(mockInputData);
            await clickSubmitButton();

            await waitFor(() =>
                expect(mockedAxios.post).toBeCalledWith(baseURL + '/Feedback', mockInputData, {
                    headers: {},
                }),
            );

            expect(screen.getByTestId('feedback-submit-spinner')).toBeInTheDocument();
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.FEEDBACK_CONFIRMATION);
        });

        it("on submit, if feedback content is empty, display an error message and don't send email", async () => {
            const mockInputData = {
                howSatisfied: SATISFACTION_CHOICES.Neither,
                respondentName: 'Jane Smith',
                respondentEmail: 'jane_smith@testing.com',
            };

            renderComponent();

            await fillInForm(mockInputData);
            await clickSubmitButton();

            await waitFor(() => {
                const errorCount = screen.getAllByText('Enter your feedback')
                expect(errorCount.length).toBe(2)
            });
            expect(mockedAxios).not.toBeCalled();
            expect(screen.queryByTestId('feedback-submit-spinner')).not.toBeInTheDocument();
        });

        it("on submit, if user haven't chosen an option for howSatisfied, display an error message and don't send email", async () => {
            const mockInputData = {
                feedbackContent: 'Mock feedback content',
                respondentName: 'Jane Smith',
                respondentEmail: 'jane_smith@testing.com',
            };

            renderComponent();

            await fillInForm(mockInputData);
            await clickSubmitButton();

            await waitFor(() => {
                const errorCount = screen.getAllByText('Select an option')
                expect(errorCount.length).toBe(2)
            });

            expect(mockedAxios).not.toBeCalled();
            expect(screen.queryByTestId('feedback-submit-spinner')).not.toBeInTheDocument();
        });

        it("on submit, if user filled in an invalid email address, display an error message and don't send email", async () => {
            const mockInputData = {
                feedbackContent: 'Mock feedback content',
                howSatisfied: SATISFACTION_CHOICES.VerySatisfied,
                respondentName: 'Jane Smith',
                respondentEmail: 'some_random_string_1234',
            };

            renderComponent();

            await fillInForm(mockInputData);
            await clickSubmitButton();

            await waitFor(() => {
                const errorCount = screen.getAllByText('Enter a valid email address')
                expect(errorCount.length).toBe(2)
            });
            expect(mockedAxios).not.toBeCalled();
            expect(screen.queryByTestId('feedback-submit-spinner')).not.toBeInTheDocument();
        });

        it('on submit, allows the respondent name and email to be blank', async () => {
            mockedAxios.post.mockImplementation(() =>
                Promise.resolve({ status: 200, data: 'Success' }),
            );
            const mockInputData = {
                feedbackContent: 'Mock feedback content',
                howSatisfied: SATISFACTION_CHOICES.VeryDissatisfied,
            };
            const expectedEmailContent = {
                ...mockInputData,
                respondentName: '',
                respondentEmail: '',
            };

            renderComponent();

            await fillInForm(mockInputData);
            await clickSubmitButton();

            await waitFor(() =>
                expect(mockedAxios.post).toBeCalledWith(
                    baseURL + '/Feedback',
                    expectedEmailContent,
                    {
                        headers: {},
                    },
                ),
            );
            expect(screen.getByTestId('feedback-submit-spinner')).toBeInTheDocument();
            expect(screen.getByRole('button')).toHaveAttribute('disabled');
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.FEEDBACK_CONFIRMATION);
        });
    });

    describe('Navigation', () => {
        it('navigates to Error page when call to feedback endpoint return 500', async () => {
            const errorResponse = {
                response: {
                    status: 500,
                    data: { message: 'An error occurred', err_code: 'SP_1001' },
                },
            };
            mockedAxios.post.mockImplementation(() => Promise.reject(errorResponse));
            const mockInputData = {
                feedbackContent: 'Mock feedback content',
                howSatisfied: SATISFACTION_CHOICES.VerySatisfied,
                respondentName: 'Jane Smith',
                respondentEmail: 'jane_smith@testing.com',
            };

            renderComponent();

            await fillInForm(mockInputData);
            await clickSubmitButton();

            await waitFor(() =>
                expect(mockedAxios.post).toBeCalledWith(baseURL + '/Feedback', mockInputData, {
                    headers: {},
                }),
            );
            expect(screen.getByTestId('feedback-submit-spinner')).toBeInTheDocument();
            expect(mockedUseNavigate).toHaveBeenCalledWith(
                routes.SERVER_ERROR + '?encodedError=WyJTUF8xMDAxIiwiMTU3NzgzNjgwMCJd',
            );
        });

        it('navigates to Session Expire page when call to feedback endpoint return 403', async () => {
            const errorResponse = {
                response: {
                    status: 403,
                    data: { message: 'Unauthorized' },
                },
            };
            mockedAxios.post.mockImplementation(() => Promise.reject(errorResponse));

            const mockInputData = {
                feedbackContent: 'Mock feedback content',
                howSatisfied: SATISFACTION_CHOICES.VerySatisfied,
                respondentName: 'Jane Smith',
                respondentEmail: 'jane_smith@testing.com',
            };

            renderComponent();

            await fillInForm(mockInputData);
            await clickSubmitButton();

            await waitFor(() =>
                expect(mockedAxios.post).toBeCalledWith(baseURL + '/Feedback', mockInputData, {
                    headers: {},
                }),
            );
            expect(screen.getByTestId('feedback-submit-spinner')).toBeInTheDocument();
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
        });

        it('navigates to feedback confirmation page when call to feedback endpoint returns 200', async () => {
            mockedAxios.post.mockImplementation(() =>
                Promise.resolve({ status: 200, data: 'Success' }),
            );
            const mockInputData = {
                feedbackContent: 'Mock feedback content',
                howSatisfied: SATISFACTION_CHOICES.VeryDissatisfied,
            };
            const expectedEmailContent = {
                ...mockInputData,
                respondentName: '',
                respondentEmail: '',
            };

            renderComponent();

            await fillInForm(mockInputData);
            await clickSubmitButton();

            await waitFor(() =>
                expect(mockedAxios.post).toBeCalledWith(
                    baseURL + '/Feedback',
                    expectedEmailContent,
                    {
                        headers: {},
                    },
                ),
            );
            expect(screen.getByTestId('feedback-submit-spinner')).toBeInTheDocument();
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.FEEDBACK_CONFIRMATION);
        });
    });
});
