import React from 'react';
import './css/main.css'
import { useLocation } from "react-router-dom";

const GeneratedPage = () => {
    const iframeSrc = `/otter_html/index.html`;
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const loading = queryParams.get("loading") === "true";
    return (
        <div>
            {loading ? (
                <div>Loading, please wait...</div>
            ) : (
                <iframe
                    title="Generated Content"
                    src={iframeSrc}
                    className="iframe"

                />
            )}
        </div>

    );
};

export default GeneratedPage;