import React, { useState, useEffect } from 'react';
import DataTable from './graph/DataTable';
import axios from "axios";

export default function BrowseResult({ isLoading, shouldLoadHTML, setIsLoading, setShouldLoadHTML }) {

    const [timestamps, setTimestamps] = useState([]);
    // const [isLoading, setIsLoading] = useState(false);


    useEffect(() => {
        // setIsLoading(true)
        axios.get("/get_all_timestamps")
            .then((response) => {

                if (response.data.hasOwnProperty('timestamps')) {
                    setTimestamps(JSON.parse(response.data['timestamps']))
                }
                // setIsLoading(false)
            })

    }, [])
    return (
        <div style={{ marginTop: 80 }}>
            {timestamps.length > 0 && <DataTable isLoading={isLoading} shouldLoadHTML={shouldLoadHTML} setIsLoading={setIsLoading} setShouldLoadHTML={setShouldLoadHTML} columns_raw={["timestamps"]} rows_raw={timestamps} />}


        </div>
    )
}