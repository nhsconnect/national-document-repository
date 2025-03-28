type Props = { status: string; className?: string };

const ProgressBar = (props: Props) => {
    const { status, className, ...elementProps } = props;
    return (
        <div className={className} {...elementProps}>
            <progress className={'progress-bar'} aria-label={status} />
            <p role="status">{status}</p>
        </div>
    );
};

export default ProgressBar;
