import React from "react";
import axios from 'axios';
import Table from "./table";
import CompilerSpeedupComparisonHistorgram from "../../histogram/CompilerSpeedupComparisonHistorgram";
import { REACT_APP_API_BASE_URL } from "../../../Constants";
const ApplicationSubTable = React.memo(({ data }) => {

    const handleButtonClick = async (timestamp) => {
        // Call your backend API here and fetch data
        const newWindow = window.open(`#/generated?loading=true`, "_blank");

        try {
            const result = await axios.post(`${REACT_APP_API_BASE_URL}/get_html_by_timestamp`, { 'timestamp': timestamp })
            //send user to new page
            newWindow.location.href = `#/generated?loading=false`;


        } catch (error) {
            console.error('Error fetching data:');
        }

    };




    const columns = [

        {
            Header: 'Action',
            id: 'button',
            Cell: ({ row }) => (
                <div className="table-action">
                    <button className="table-action-button" onClick={() => handleButtonClick(row.original.run_timestamp)}>See OV Report</button>
                </div>

            ),
        },
        { Header: 'Timestamp', accessor: 'run_timestamp' },
        { Header: 'GFlops', accessor: 'gflops' },
        { Header: 'Compiler', accessor: 'compiler' },
        { Header: 'Time', accessor: 'time' },
    ];

    //used to show only data for ov in the table
    const filterDataForOV = (data) => {
        return data.filter(item => item.has_ov);
    };
    const filteredData = filterDataForOV(data);


    return (
        <div className="center-children">
            <CompilerSpeedupComparisonHistorgram data={data} />
            {/* <Table
                data={filteredData}
                columns={columns}
                defaultPageSize={5}
            /> */}
        </div>
    );
})

export default ApplicationSubTable;