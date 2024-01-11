import { act, render, screen, waitFor } from '@testing-library/react';
import FeedbackPage from './FeedbackPage';
import { FORM_FIELDS, SATISFACTION_CHOICES, FormData } from '../../types/pages/feedbackPage/types';
import userEvent from '@testing-library/user-event';
import sendEmail from '../../helpers/requests/sendEmail';

jest.mock('../../helpers/requests/sendEmail');
const mockSendEmail = sendEmail as jest.Mock;

describe('<Feedbackpage />', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the page header', () => {
        render(<FeedbackPage />);

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

        render(<FeedbackPage />);

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
        render(<FeedbackPage />);

        expect(screen.getByRole('button', { name: 'Send feedback' })).toBeInTheDocument();
    });

    describe('user interactions', () => {
        it('on submit, call sendEmail() with the data that user had filled in', async () => {
            const mockInputData = {
                feedbackContent: 'Mock feedback content',
                howSatisfied: SATISFACTION_CHOICES.VerySatisfied,
                respondentName: 'Jane Smith',
                respondentEmail: 'jane_smith@testing.com',
            };
            mockSendEmail.mockReturnValue(Promise.resolve());

            render(<FeedbackPage />);

            act(() => {
                fillInData(mockInputData);
                clickSubmitButton();
            });

            await waitFor(() => expect(mockSendEmail).toBeCalledWith(mockInputData));
        });

        it('display an error message on submit if feedback content is empty', async () => {
            const mockInputData = {
                howSatisfied: SATISFACTION_CHOICES.VerySatisfied,
                respondentName: 'Jane Smith',
                respondentEmail: 'jane_smith@testing.com',
            };
            mockSendEmail.mockReturnValue(Promise.resolve());

            render(<FeedbackPage />);

            act(() => {
                fillInData(mockInputData);
                clickSubmitButton();
            });

            await waitFor(() => {
                expect(screen.getByText('Please enter your feedback')).toBeInTheDocument();
            });
        });

        it('display an error message on submit if user have not chosen a howSatisfied option', async () => {
            const mockInputData = {
                feedbackContent: 'Mock feedback content',
                respondentName: 'Jane Smith',
                respondentEmail: 'jane_smith@testing.com',
            };
            mockSendEmail.mockReturnValue(Promise.resolve());

            render(<FeedbackPage />);

            act(() => {
                fillInData(mockInputData);
                clickSubmitButton();
            });

            await waitFor(() => {
                expect(screen.getByText('Please select an option')).toBeInTheDocument();
            });
        });
    });
});

const clickSubmitButton = () => {
    userEvent.click(screen.getByRole('button', { name: 'Send feedback' }));
};

const fillInData = (data: Partial<FormData>) => {
    for (const [fieldName, value] of Object.entries(data)) {
        if (fieldName === FORM_FIELDS.howSatisfied) {
            userEvent.click(screen.getByRole('radio', { name: value }));
        } else {
            userEvent.click(screen.getByTestId(fieldName));
            userEvent.type(screen.getByTestId(fieldName), value);
        }
    }
};
