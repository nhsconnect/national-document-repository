import { FormGroup, Form, Button } from 'nhsuk-react-components';
import { FieldValues, useForm } from 'react-hook-form';

type LoginFormData = {
    username: string;
    password: string;
};
const MockCis2LoginPage = () => {
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginFormData>({
        reValidateMode: 'onSubmit',
    });
    const submit = async (fieldValues: FieldValues) => {
        const { username, password } = fieldValues;

        if (username && password) {
            // Save or send login details here
            console.log('Username:', username);
            console.log('Password:', password);
            // await submitLoginDetails(username,password)
        }
    };

    return (
        <div className="nhsuk-main-wrapper--s">
            <div className="nhsuk-grid-row">
                <div className="nhsuk-grid-column-two-thirds">
                    <Form onSubmit={handleSubmit(submit)}>
                        <FormGroup>
                            <div className="form-label-group">
                                <div className="nhsuk-form-group position-relative">
                                    <label htmlFor="username">Username</label>
                                    <input
                                        className="nhsuk-input"
                                        type="text"
                                        id="username"
                                        {...register('username', { required: true })}
                                    />
                                    {errors.username && (
                                        <span className="nhsuk-error-message">
                                            Username is required
                                        </span>
                                    )}
                                </div>
                            </div>
                        </FormGroup>
                        <FormGroup>
                            <div className="form-label-group">
                                <div className="nhsuk-form-group position-relative">
                                    <label htmlFor="password">Password</label>
                                    <input
                                        className="nhsuk-input"
                                        type="password"
                                        id="password"
                                        {...register('password', { required: true })}
                                    />
                                    {errors.password && (
                                        <span className="nhsuk-error-message">
                                            Password is required
                                        </span>
                                    )}
                                </div>
                            </div>
                            <Button type="submit" id="submit-login-details">
                                Continue
                            </Button>
                        </FormGroup>
                    </Form>
                </div>
            </div>
        </div>
    );
};

export default MockCis2LoginPage;
