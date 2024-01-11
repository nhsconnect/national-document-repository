import { Button, Fieldset, Input, Radios, Textarea } from 'nhsuk-react-components';

const satisfactionOptions = [
    'Very satisfied',
    'Satisfied',
    'Neither satisfied or dissatisfied',
    'Dissatisfied',
    'Very dissatisfied',
];

function FeedbackPage() {
    return (
        <>
            <h1>Give feedback on accessing Lloyd George digital patient records</h1>

            <form onSubmit={() => {}}>
                <Fieldset>
                    <Fieldset.Legend size="l">What is your feedback?</Fieldset.Legend>

                    <Textarea
                        id="feedback-content"
                        label="Tell us how we could improve this service or explain your experience using it. You
                can also give feedback about a specific page or section in the service."
                        name="feedback-content"
                        rows={7}
                    />
                </Fieldset>

                <Fieldset>
                    <Fieldset.Legend size="l">
                        How satisfied were you with your overall experience of using this service?
                    </Fieldset.Legend>
                    <Radios id="select-how-satisfied" name="how-satisfied">
                        {satisfactionOptions.map((choice) => (
                            <Radios.Radio key={choice} value={choice}>
                                {choice}
                            </Radios.Radio>
                        ))}
                    </Radios>
                </Fieldset>

                <Fieldset>
                    <Fieldset.Legend size="l">Leave your details (optional)</Fieldset.Legend>

                    <p>
                        If you're happy to speak to us about your feedback so we can improve this
                        service, please leave your details below.
                    </p>

                    <Input id="respondent-name" label="Your name" name="name" />

                    <Input
                        id="respondent-email"
                        label="Your email address"
                        name="email"
                        hint="We’ll only use this to speak to you about your feedback"
                    />
                </Fieldset>

                <Button type="submit" id="feedback-submit-btn" data-testid="feedback-submit-btn">
                    Send feedback
                </Button>
            </form>
        </>
    );
}

export default FeedbackPage;
