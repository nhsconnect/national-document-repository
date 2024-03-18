import React from 'react';

function LinkButton(props: React.HTMLProps<HTMLButtonElement>) {
    return (
        <button
            {...props}
            className={props.className ? `lloydgeorge_link ${props.className}` : 'lloydgeorge_link'}
            type="button"
        />
    );
}

export default LinkButton;
