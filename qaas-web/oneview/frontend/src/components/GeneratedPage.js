import React from 'react';
import './css/main.css'
import { useLocation } from "react-router-dom";

const GeneratedPage = () => {
    const iframeSrc = `http://localhost:81/otter_html/index.html`;
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const loading = queryParams.get("loading") === "true";
    console.log("iframeSrc:", iframeSrc);

    return (
        <div>
            {loading ? (
                <div>iframe URL: {iframeSrc} Loading124, please wait...</div>
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