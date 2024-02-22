import React, { useState, useEffect } from 'react';
import axios from "axios";
import ApplicationTable from '../graph/table/job_submission_table/ApplicationTable';
// import CompilerComparisonHistogram from '../graph/histogram/CompilerComparisonHistogram';
export default function BrowseResult() {

    const [tableData, setTableData] = useState([]);
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_job_submission_results`)
            .then((response) => {

                const rawData = response.data

                setTableData(rawData);



            })

    }, [])

    return (
        <div >
            test
            <ApplicationTable data={tableData} />

            {/* <CompilerComparisonHistogram /> */}


        </div>
    )
}