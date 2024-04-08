import {
    FORM_FIELDS,
    FormData,
    SATISFACTION_CHOICES,
    SUBMISSION_STAGE,
} from '../../../types/pages/feedbackPage/types';
import React, { Dispatch } from 'react';
import { SubmitHandler, useForm, UseFormRegisterReturn } from 'react-hook-form';
import isEmail from 'validator/lib/isEmail';

import sendEmail from '../../../helpers/requests/sendEmail';
import { Button, Fieldset, Input, Radios, Textarea } from 'nhsuk-react-components';
import SpinnerButton from '../../generic/spinnerButton/SpinnerButton';
import { routes } from '../../../types/generic/routes';
import { useNavigate } from 'react-router-dom';
import { errorToParams } from '../../../helpers/utils/errorToParams';
import { AxiosError } from 'axios';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';

export type Props = {
    stage: SUBMISSION_STAGE;
    setStage: Dispatch<SUBMISSION_STAGE>;
};

function FeedbackForm({ stage, setStage }: Props) {
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const {
        handleSubmit,
        register,
        formState: { errors },
    } = useForm<FormData>({
        reValidateMode: 'onSubmit',
    });
    const navigate = useNavigate();

    const submit: SubmitHandler<FormData> = async (formData) => {
        setStage(SUBMISSION_STAGE.Submitting);
        try {
            await sendEmail({ formData, baseUrl, baseHeaders });
            setStage(SUBMISSION_STAGE.Successful);
        } catch (e) {
            const error = e as AxiosError;
            if (error.response?.status === 403) {
                navigate(routes.SESSION_EXPIRED);
            }
            navigate(routes.SERVER_ERROR + errorToParams(error));
        }
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
                if (value === '' || isEmail(value)) {
                    return true; // accept either blank or a valid email
                }
                return 'Enter a valid email address';
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
                    <p>
                        When submitting your details using our feedback form, any personal
                        information you give to us will be processed in accordance with the UK
                        General Data Protection Regulation (GDPR) 2018.
                    </p>
                    <p>
                        We use the information you submitted to process your request and provide
                        relevant information or services you have requested. This will help support
                        us in developing this service.
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
                    <Button type="submit" id="submit-feedback">
                        Send feedback
                    </Button>
                ) : (
                    <SpinnerButton
                        id="feedback-submit-spinner"
                        status="Submitting..."
                        disabled={true}
                    />
                )}
            </form>
        </div>
    );
}

export default FeedbackForm;
