import { FORM_FIELDS, FormData } from '../../types/pages/feedbackPage/types';
import userEvent from '@testing-library/user-event';
import { screen } from '@testing-library/react';

export const fillInForm = (data: Partial<FormData>) => {
    for (const [fieldName, value] of Object.entries(data)) {
        if (fieldName === FORM_FIELDS.howSatisfied) {
            userEvent.click(screen.getByRole('radio', { name: value }));
        } else {
            userEvent.click(screen.getByTestId(fieldName));
            userEvent.type(screen.getByTestId(fieldName), value);
        }
    }
};
