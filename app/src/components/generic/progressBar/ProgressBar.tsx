type Props = { status: string };

const ProgressBar = (props: Props) => {
    const { status, ...elementProps } = props;
    return (
        <div {...elementProps}>
            <progress className={'progress-bar'} aria-label={status} />
            <p role="status">{status}</p>
        </div>
    );
};

export default ProgressBar;
