import { Button, Fieldset, Input, Radios, Textarea } from 'nhsuk-react-components';
import { SubmitHandler, useForm, UseFormRegisterReturn } from 'react-hook-form';

type FormData = {
    feedbackContent: string;
    howSatisfied: string;
    respondentName: string;
    respondentEmail: string;
};

const choicesForHowSatisfied = [
    'Very satisfied',
    'Satisfied',
    'Neither satisfied or dissatisfied',
    'Dissatisfied',
    'Very dissatisfied',
];

function FeedbackPage() {
    const {
        handleSubmit,
        register,
        formState: { errors },
    } = useForm<FormData>();

    const sendEmail = async (formData: FormData) => {
        console.log(`sending feedback from user by email: ${JSON.stringify(formData)}}`);
        return { status: 200 };
    };
    const submit: SubmitHandler<FormData> = async (formData) => {
        sendEmail(formData)
            .then(() => {
                console.log('Successfully sent email');
                console.log('will move to confirmation screen');
            })
            .catch((e) => console.error(`got error: {e}`));
    };

    const renameRefKey = (props: UseFormRegisterReturn, refKey: string) => {
        const { ref, ...otherProps } = props;
        return {
            [refKey]: ref,
            ...otherProps,
        };
    };

    const feedbackContentProps = renameRefKey(
        register('feedbackContent', { required: 'Please enter your feedback here' }),
        'textareaRef',
    );
    const howSatisfiedProps = renameRefKey(
        register('howSatisfied', { required: 'Please select an option' }),
        'inputRef',
    );
    const respondentNameProps = renameRefKey(register('respondentName'), 'inputRef');
    const respondentEmailProps = renameRefKey(register('respondentEmail'), 'inputRef');

    return (
        <div id="feedback-form">
            <h1>Give feedback on accessing Lloyd George digital patient records</h1>

            <form onSubmit={handleSubmit(submit)}>
                <Fieldset>
                    <Fieldset.Legend size="m">What is your feedback?</Fieldset.Legend>
                    <Textarea
                        id="feedback-content"
                        label="Tell us how we could improve this service or explain your experience using it. You
                can also give feedback about a specific page or section in the service."
                        rows={7}
                        error={errors.feedbackContent?.message}
                        {...feedbackContentProps}
                    />
                </Fieldset>

                <Fieldset>
                    <Fieldset.Legend size="m">
                        How satisfied were you with your overall experience of using this service?
                    </Fieldset.Legend>
                    <Radios id="select-how-satisfied" error={errors.howSatisfied?.message}>
                        {choicesForHowSatisfied.map((choice, i) => (
                            <Radios.Radio key={i} value={choice} {...howSatisfiedProps}>
                                {choice}
                            </Radios.Radio>
                        ))}
                    </Radios>
                </Fieldset>

                <Fieldset>
                    <Fieldset.Legend size="m">Leave your details (optional)</Fieldset.Legend>

                    <p>
                        If you're happy to speak to us about your feedback so we can improve this
                        service, please leave your details below.
                    </p>

                    <Input id="respondent-name" label="Your name" {...respondentNameProps} />

                    <Input
                        id="respondent-email"
                        label="Your email address"
                        hint="We’ll only use this to speak to you about your feedback"
                        {...respondentEmailProps}
                    />
                </Fieldset>

                <Button type="submit" id="feedback-submit-btn" data-testid="feedback-submit-btn">
                    Send feedback
                </Button>
            </form>
        </div>
    );
}

export default FeedbackPage;
