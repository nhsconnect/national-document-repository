import { FormGroup } from 'nhsuk-react-components';

const MockCis2LoginPage = () => {
    return (
        <div className="nhsuk-main-wrapper--s">
            <div className="nhsuk-grid-row">
                <div className="nhsuk-grid-column-two-thirds">
                    <FormGroup>
                        <div className="form-label-group">
                            <div className="nhsuk-form-group position-relative">
                                <label>User Name</label>
                                <input className="nhsuk-input"></input>
                            </div>
                        </div>
                        <div className="form-label-group">
                            <div className="nhsuk-form-group position-relative">
                                <label>Password</label>
                                <input className="nhsuk-input"></input>
                            </div>
                        </div>
                        <div className="form-label-group">
                            <button className="nhsuk-button">Continue</button>
                        </div>
                    </FormGroup>
                </div>
            </div>
        </div>
    );
};

export default MockCis2LoginPage;
