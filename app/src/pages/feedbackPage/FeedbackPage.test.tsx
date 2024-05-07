import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import { SATISFACTION_CHOICES, SUBMISSION_STAGE } from '../../types/pages/feedbackPage/types';
import FeedbackPage from './FeedbackPage';
import { fillInForm } from '../../helpers/test/formUtils';
import { routes } from '../../types/generic/routes';

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

jest.mock('react-router', () => ({
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

    it('renders the page header', () => {
        renderComponent();

        expect(
            screen.getByRole('heading', {
                name: 'Give feedback on accessing Lloyd George digital patient records',
            }),
        ).toBeInTheDocument();
    });

    it('renders the feedback form content', () => {
        const contentStrings = [
            'What is your feedback?',
            'Tell us how we could improve this service or explain your experience using it. ' +
                'You can also give feedback about a specific page or section in the service.',
            'How satisfied were you with your overall experience of using this service?',
            'If you’re happy to speak to us about your feedback so we can improve this service,' +
                ' please leave your details below.',
            'Your name',
            'Your email address',
            'We’ll only use this to speak to you about your feedback',
        ];

        renderComponent();

        contentStrings.forEach((s) => {
            expect(screen.getByText(s)).toBeInTheDocument();
        });

        const textboxLabels = [/Tell us how we could improve/, 'Your name', 'Your email address'];

        textboxLabels.forEach((label) => {
            expect(screen.getByRole('textbox', { name: label })).toBeInTheDocument();
        });

        const radioLabels = Object.values(SATISFACTION_CHOICES);
        radioLabels.forEach((label) => {
            expect(screen.getByRole('radio', { name: label })).toBeInTheDocument();
        });
    });

    it('renders a primary button for submit', () => {
        renderComponent();

        expect(screen.getByRole('button', { name: 'Send feedback' })).toBeInTheDocument();
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
            expect(screen.getByText('Submitting...')).toBeInTheDocument();
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
            expect(screen.queryByText('Submitting...')).not.toBeInTheDocument();
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
            expect(screen.queryByText('Submitting...')).not.toBeInTheDocument();
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
            expect(screen.queryByText('Submitting...')).not.toBeInTheDocument();
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
            expect(screen.getByText('Submitting...')).toBeInTheDocument();
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
            expect(screen.getByText('Submitting...')).toBeInTheDocument();
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
            expect(screen.getByText('Submitting...')).toBeInTheDocument();
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
            expect(screen.getByText('Submitting...')).toBeInTheDocument();
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.FEEDBACK_CONFIRMATION);
        });
    });
});
