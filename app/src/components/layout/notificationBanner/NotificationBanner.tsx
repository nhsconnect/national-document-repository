import { ReactNode } from 'react';

type Props = {
    title: string;
    children: ReactNode;
    className: string;
};

const NotificationBanner = ({ title, children, className }: Props) => {
    return (
        <div className={`govuk-notification-banner ${className}`}>
            <div className="govuk-notification-banner__header">
                <h3
                    className="govuk-notification-banner__title"
                    data-testid="notification-banner-title"
                >
                    {title}
                </h3>
            </div>
            <div
                className="govuk-notification-banner__content"
                data-testid="notification-banner-content"
            >
                {children}
            </div>
        </div>
    );
};

export default NotificationBanner;
