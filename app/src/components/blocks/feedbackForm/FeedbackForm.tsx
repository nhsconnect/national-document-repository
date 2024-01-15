import {
    FORM_FIELDS,
    FormData,
    SATISFACTION_CHOICES,
    SUBMISSION_STAGE,
} from '../../../types/pages/feedbackPage/types';
import React, { Dispatch, useState } from 'react';
import { SubmitHandler, useForm, UseFormRegisterReturn } from 'react-hook-form';
import isEmail from 'validator/lib/isEmail';

import sendEmail from '../../../helpers/requests/sendEmail';
import { Button, Fieldset, Input, Radios, Textarea } from 'nhsuk-react-components';
import SpinnerButton from '../../generic/spinnerButton/SpinnerButton';

export type Props = {
    stage: SUBMISSION_STAGE;
    setStage: Dispatch<SUBMISSION_STAGE>;
};

function FeedbackForm({ stage, setStage }: Props) {
    const {
        handleSubmit,
        register,
        formState: { errors },
    } = useForm<FormData>({
        reValidateMode: 'onSubmit',
    });

    // a placeholder to test form submit until we got the confirmation page in place
    const [result, setResult] = useState<FormData | null>(null);

    const submit: SubmitHandler<FormData> = async (formData) => {
        setStage(SUBMISSION_STAGE.Submitting);

        sendEmail(formData)
            .then(() => {
                setStage(SUBMISSION_STAGE.Successful);
                setResult(formData);
            })
            .catch((e) => {
                setStage(SUBMISSION_STAGE.Failure);
            });
    };

    const renameRefKey = (props: UseFormRegisterReturn, newRefKey: string) => {
        const { ref, ...otherProps } = props;
        return {
            [newRefKey]: ref,
            ...otherProps,
        };
    };

    const feedbackContentProps = renameRefKey(
        register(FORM_FIELDS.FeedbackContent, {
            required: 'Please enter your feedback',
        }),
        'textareaRef',
    );
    const howSatisfiedProps = renameRefKey(
        register(FORM_FIELDS.HowSatisfied, { required: 'Please select an option' }),
        'inputRef',
    );
    const respondentNameProps = renameRefKey(register(FORM_FIELDS.RespondentName), 'inputRef');
    const respondentEmailProps = renameRefKey(
        register(FORM_FIELDS.RespondentEmail, {
            validate: (value) => {
                if (value === '') {
                    return true; // allow email address to be blank
                }
                return isEmail(value) ? true : 'Enter a valid email address';
            },
        }),
        'inputRef',
    );

    return (
        <div id="feedback-form">
            <h1>Give feedback on accessing Lloyd George digital patient records</h1>

            <form onSubmit={handleSubmit(submit)}>
                <Fieldset>
                    <Fieldset.Legend size="m">What is your feedback?</Fieldset.Legend>
                    <Textarea
                        data-testid={FORM_FIELDS.FeedbackContent}
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
                        {Object.values(SATISFACTION_CHOICES).map((choice) => (
                            <Radios.Radio key={choice} value={choice} {...howSatisfiedProps}>
                                {choice}
                            </Radios.Radio>
                        ))}
                    </Radios>
                </Fieldset>

                <Fieldset>
                    <Fieldset.Legend size="m">Leave your details (optional)</Fieldset.Legend>

                    <p>
                        If you’re happy to speak to us about your feedback so we can improve this
                        service, please leave your details below.
                    </p>

                    <Input
                        label="Your name"
                        data-testid={FORM_FIELDS.RespondentName}
                        autoComplete="name"
                        spellCheck={false}
                        {...respondentNameProps}
                    />

                    <Input
                        label="Your email address"
                        hint="We’ll only use this to speak to you about your feedback"
                        data-testid={FORM_FIELDS.RespondentEmail}
                        autoComplete="email"
                        spellCheck={false}
                        error={errors.respondentEmail?.message}
                        {...respondentEmailProps}
                    />
                </Fieldset>
                {stage !== SUBMISSION_STAGE.Submitting ? (
                    <Button type="submit">Send feedback</Button>
                ) : (
                    <SpinnerButton
                        id="feedback-submit-spinner"
                        status="Submitting..."
                        disabled={true}
                    />
                )}
            </form>
            {/* to be removed when we got the confirmation page in place. */}
            {result && (
                <p>{`[Placeholder] called sendEmail() with data: \n${JSON.stringify(result)}`}</p>
            )}
        </div>
    );
}

export default FeedbackForm;
