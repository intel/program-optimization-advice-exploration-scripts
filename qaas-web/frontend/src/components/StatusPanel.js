import React from 'react';

export default function StatusPanel({msg}) {
    return (
        <div style={{marginTop:80}}>
            <div>StatusPanel</div>
            {msg}
        </div>
    )
}