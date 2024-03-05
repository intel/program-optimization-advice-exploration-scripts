//this context is used to keep global message
import React, { createContext, useContext, useState, useEffect } from 'react';

const initialContextState = {
    statusMsg: '',
    SSEStatus: false,
    setSSEStatus: () => { },
    startSSEConnection: () => { },
    closeSSEConnection: () => { },
};

const SSEContext = createContext(initialContextState);

export const SSEProvider = ({ children }) => {
    const [statusMsg, setStatusMsg] = useState(initialContextState.statusMsg);
    const [sse, setSse] = useState(null); //   SSE connection
    const [SSEStatus, setSSEStatus] = useState(initialContextState.SSEStatus);
    // start SSE connection
    const startSSEConnection = () => {
        const newSse = new EventSource(`${process.env.REACT_APP_API_BASE_URL}/stream`);
        newSse.onmessage = e => {
            setStatusMsg(e.data);
        };
        newSse.addEventListener('ping', e => {
            console.log("set sse", e.data)
            setStatusMsg(e.data)
        })
        newSse.onerror = e => {
            newSse.close();
        };
        setSse(newSse);
    };

    // close SSE connection
    const closeSSEConnection = () => {
        if (sse) {
            sse.close();
            setSse(null);
        }
    };

    // cleanup on unmount
    useEffect(() => {
        return () => {
            closeSSEConnection();
        };
    }, []);

    return (
        <SSEContext.Provider value={{ statusMsg, SSEStatus, setSSEStatus, startSSEConnection, closeSSEConnection }}>
            {children}
        </SSEContext.Provider>
    );
};


export const useSSE = () => useContext(SSEContext);
