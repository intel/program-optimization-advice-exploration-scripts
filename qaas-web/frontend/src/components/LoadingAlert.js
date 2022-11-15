import React from 'react';

export default function LoadingAlert(props) {
    const container={
        "width": "800px",
        "hight": "400px",
        "background-color":"red"
    }
    return (
        <div class={container}>
            {props.text}
        </div>
    );
}