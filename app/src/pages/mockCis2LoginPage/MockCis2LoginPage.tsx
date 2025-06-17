import { FormGroup, Form, Button } from 'nhsuk-react-components';
import { useForm } from 'react-hook-form';
import { routes } from '../../types/generic/routes';
import { OrganisationDetails } from '../../types/generic/organisationDetails';
import { useNavigate } from 'react-router-dom';
import { AxiosError } from 'axios';
import { errorToParams } from '../../helpers/utils/errorToParams';
import { useOrganisationDetailsContext } from '../../providers/OrganisationProvider/OrganisationProvider';

type LoginFormData = {
    username: string;
    password: string;
};

const MockCis2LoginPage = () => {
    const navigate = useNavigate();
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginFormData>({
        reValidateMode: 'onSubmit',
    });
    const [, setOrganisationDetails] = useOrganisationDetailsContext();
    const submit = async (fieldValues: LoginFormData) => {
        const { username, password } = fieldValues;

        if (username && password) {
            // Save or send login details here
            console.log('Username:', username);
            console.log('Password:', password);
            // await submitLoginDetails(username,password)
            try {
                //     const organisationDetails = await getOrganisationDetails({
                //     username,
                //     password,
                //     baseUrl,
                //     baseHeaders,
                // });

                const organisationDetails: OrganisationDetails[] = [
                    { role: 'GP Admin', odsCode: 'A12345', practiceName: 'Sunrise Health Centre' },
                    {
                        role: 'Receptionist',
                        odsCode: 'B67890',
                        practiceName: 'Moonlight Medical Practice',
                    },
                    {
                        role: 'Practice Manager',
                        odsCode: 'C13579',
                        practiceName: 'Riverbank Surgery',
                    },
                ];
                // [OrganisationDetails]
                //need to figure out how to pass the response
                setOrganisationDetails(organisationDetails);
                navigate(routes.MOCK_ROLE_SELECT_PAGE);
            } catch (e) {
                const error = e as AxiosError;
                navigate(routes.SERVER_ERROR + errorToParams(error));
            }
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
                        </FormGroup>
                        <Button type="submit" id="submit-login-details">
                            Continue
                        </Button>
                    </Form>
                </div>
            </div>
        </div>
    );
};

export default MockCis2LoginPage;
