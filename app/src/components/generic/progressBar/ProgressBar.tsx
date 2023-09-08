type Props = { status: string };

const ProgressBar = (props: Props) => {
    return (
        <>
            <progress aria-label={props.status} />
            <p role="status">{props.status}</p>
        </>
    );
};

export default ProgressBar;
