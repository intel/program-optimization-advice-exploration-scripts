import React from 'react';

export default function StatusPanel({msg}) {
    console.log("meg in status panel",msg)
    return (
        <div style={{marginTop:80}}>
            <div>StatusPanel</div>
            <p>{msg}</p>
        </div>
    )
}