import React from 'react';

function LinkButton(props: React.HTMLProps<HTMLButtonElement>) {
    const classNames = 'lloydgeorge_link align-center pt-3 pb-3 pl-3 pr-3';
    return (
        <button
            {...props}
            className={props.className ? `${classNames} ${props.className}` : classNames}
            type="button"
        >
            <div>{props.children}</div>
        </button>
    );
}

export default LinkButton;
