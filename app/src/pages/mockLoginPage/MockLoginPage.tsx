import { FormGroup, Form, Button } from 'nhsuk-react-components';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { routes } from '../../types/generic/routes';
import { mock } from 'node:test';

type LoginFormData = {
    key: string;
    odsCode: string;
    repositoryRole: string;
};

const MockLoginPage = () => {
    const [key, setKey] = useState('');
    const [odsCode, setOdsCode] = useState('');
    const [repositoryRole, setRepositoryRole] = useState('');
    const navigate = useNavigate();

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        console.log({ key, odsCode, repositoryRole });

        const formData: LoginFormData = { key, odsCode, repositoryRole };
        const json = JSON.stringify(formData);

        const encodedData = encodeURIComponent(json);
        const mockState = 'mock';

        const queryParams = new URLSearchParams();
        queryParams.append('code', encodedData);
        queryParams.append('state', mockState);

        const full = `${routes.AUTH_CALLBACK}?${queryParams.toString()}`;
        console.log(full);
        navigate(`${routes.AUTH_CALLBACK}?${queryParams.toString()}`);
    };

    return (
        <div className="nhsuk-main-wrapper--s">
            <div className="nhsuk-grid-row">
                <div className="nhsuk-grid-column-two-thirds">
                    <Form onSubmit={handleSubmit}>
                        <FormGroup>
                            <div className="form-label-group">
                                <div className="nhsuk-form-group position-relative">
                                    <label className="nhsuk-label" htmlFor="key">
                                        Key
                                    </label>
                                    <input
                                        className="nhsuk-input"
                                        id="key"
                                        name="key"
                                        type="text"
                                        value={key}
                                        onChange={(e) => setKey(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>
                        </FormGroup>
                        <FormGroup>
                            <div className="form-label-group">
                                <div className="nhsuk-form-group position-relative">
                                    <label className="nhsuk-label" htmlFor="odsCode">
                                        Ods Code
                                    </label>
                                    <input
                                        className="nhsuk-input"
                                        id="odsCode"
                                        name="odsCode"
                                        type="text"
                                        value={odsCode}
                                        onChange={(e) => setOdsCode(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>
                        </FormGroup>
                        <FormGroup>
                            <div className="form-label-group">
                                <div className="nhsuk-form-group position-relative">
                                    <label className="nhsuk-label" htmlFor="repositoryRole">
                                        {' '}
                                        Select Repository role
                                    </label>
                                    <select
                                        className="nhsuk-select"
                                        id="repositoryRole"
                                        name="repositoryRole"
                                        value={repositoryRole}
                                        onChange={(e) => setRepositoryRole(e.target.value)}
                                        required
                                    >
                                        <option value="GP Admin">GP Admin</option>
                                        <option value="GP Clinical">GP Clinical</option>
                                        <option value="PCSE">PCSE</option>
                                        <option value="No Role">No Role</option>
                                    </select>
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

export default MockLoginPage;
