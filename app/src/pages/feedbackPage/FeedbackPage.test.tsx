import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import { SATISFACTION_CHOICES } from '../../types/pages/feedbackPage/types';
import FeedbackPage from './FeedbackPage';
import { fillInForm } from '../../helpers/test/formUtils';
import { routes } from '../../types/generic/routes';
import { runAxeTest } from '../../helpers/test/axeTestHelper';

jest.mock('axios');
jest.mock('../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../helpers/hooks/useBaseAPIHeaders');
const mockedUseNavigate = jest.fn();
const mockedAxios = axios as jest.Mocked<typeof axios>;
const mockedBaseURL = useBaseAPIUrl as jest.Mock;
const baseURL = 'http://test';
jest.mock('moment', () => {
    return () => jest.requireActual('moment')('2020-01-01T00:00:00.000Z');
});

jest.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));

const clickSubmitButton = () => {
    userEvent.click(screen.getByRole('button', { name: 'Send feedback' }));
};

const renderComponent = () => {
    return render(<FeedbackPage />);
};

describe('<FeedbackPage />', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedBaseURL.mockReturnValue(baseURL);
    });
    afterEach(() => {
        jest.clearAllMocks();
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

            act(() => {
                fillInForm(mockInputData);
                clickSubmitButton();
            });

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

            act(() => {
                fillInForm(mockInputData);
                clickSubmitButton();
            });

            await waitFor(() => {
                expect(screen.getByText('Please enter your feedback')).toBeInTheDocument();
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

            act(() => {
                fillInForm(mockInputData);
                clickSubmitButton();
            });

            await waitFor(() => {
                expect(screen.getByText('Please select an option')).toBeInTheDocument();
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

            act(() => {
                fillInForm(mockInputData);
                clickSubmitButton();
            });

            await waitFor(() => {
                expect(screen.getByText('Enter a valid email address')).toBeInTheDocument();
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

            act(() => {
                fillInForm(mockInputData);
                clickSubmitButton();
            });

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

            act(() => {
                fillInForm(mockInputData);
                clickSubmitButton();
            });

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

            act(() => {
                fillInForm(mockInputData);
                clickSubmitButton();
            });

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

            act(() => {
                fillInForm(mockInputData);
                clickSubmitButton();
            });

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
