import React from 'react';
import { Footer as NHSFooter } from 'nhsuk-react-components';
import { useNavigate } from 'react-router';
import { routes } from '../../../types/generic/routes';

function Footer() {
    const navigate = useNavigate();
    return (
        <NHSFooter>
            <NHSFooter.List>
                <NHSFooter.ListItem
                    href={'#'}
                    data-testid="privacy-link"
                    onClick={(e) => {
                        e.preventDefault();
                        navigate(routes.PRIVACY_POLICY);
                    }}
                >
                    Privacy notice
                </NHSFooter.ListItem>
            </NHSFooter.List>
            <NHSFooter.Copyright>&copy; {'Crown copyright'}</NHSFooter.Copyright>
        </NHSFooter>
    );
}

export default Footer;
