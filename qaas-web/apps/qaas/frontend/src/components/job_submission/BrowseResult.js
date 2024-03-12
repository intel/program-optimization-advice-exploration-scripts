import React, { useState, useEffect } from 'react';
import axios from "axios";
import { useLocation } from 'react-router-dom';
import ApplicationTable from '../graph/table/job_submission_table/ApplicationTable';
import StatusPanel from './StatusPanel';
import { useSSE } from '../contexts/SSEContext';
// import CompilerComparisonHistogram from '../graph/histogram/CompilerComparisonHistogram';
export default function BrowseResult() {


    const [tableData, setTableData] = useState([]);
    const location = useLocation();
    const { statusMsg, SSEStatus } = useSSE();


    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_job_submission_results`)
            .then((response) => {

                const rawData = response.data

                setTableData(rawData);



            })

    }, [])

    return (
        <div >
            <ApplicationTable data={tableData} />

            {/* only show status panel when sse is on */}
            {statusMsg && <StatusPanel msg={statusMsg} />}
        </div>
    )
}