import { FormGroup, Form } from 'nhsuk-react-components';
import { useState } from 'react';

const MockCis2LoginPage = () => {
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
    };

    return (
        <div className="nhsuk-main-wrapper--s">
            <div className="nhsuk-grid-row">
                <div className="nhsuk-grid-column-two-thirds">
                    <Form onSubmit={handleSubmit}>
                        <FormGroup>
                            <div className="form-label-group">
                                <div className="nhsuk-form-group position-relative">
                                    <label htmlFor="username">Username</label>
                                    <input
                                        className="nhsuk-input"
                                        type="text"
                                        id="username"
                                        onChange={(e) => setUsername(e.target.value)}
                                    ></input>
                                </div>
                            </div>
                        </FormGroup>
                        <FormGroup>
                            <div className="form-label-group">
                                <div className="nhsuk-form-group position-relative">
                                    <label htmlFor="password">Password</label>
                                    <input
                                        className="nhsuk-input"
                                        type="text"
                                        id="password"
                                        onChange={(e) => setPassword(e.target.value)}
                                    ></input>
                                </div>
                            </div>
                            <div className="form-label-group">
                                <button className="nhsuk-button">Continue</button>
                            </div>
                        </FormGroup>
                    </Form>
                </div>
            </div>
        </div>
    );
};

export default MockCis2LoginPage;
