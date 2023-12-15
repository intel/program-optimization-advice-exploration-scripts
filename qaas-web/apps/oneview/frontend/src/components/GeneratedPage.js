import React from 'react';
import './css/main.css'
import { useLocation } from "react-router-dom";

const GeneratedPage = () => {
    const myhost = window.location.hostname
    const myprotocol = window.location.protocol
    const myport = window.location.port

    const iframeSrc = `${myprotocol}//${myhost}:${myport}/otter_html/index.html`;
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const loading = queryParams.get("loading") === "true";
    return (
        <div>
            {loading ? (
                <div>iframe URL: {iframeSrc} Loading, please wait...</div>
            ) : (

                <div>
                    <div>iframe URL: {iframeSrc}</div>
                    <iframe
                        title="Generated Content"
                        src={iframeSrc}
                        className="iframe"
                        onError={(e) => console.error("Error loading iframe:", e)}
                    />
                </div>
            )}
        </div>

    );
};

export default GeneratedPage;