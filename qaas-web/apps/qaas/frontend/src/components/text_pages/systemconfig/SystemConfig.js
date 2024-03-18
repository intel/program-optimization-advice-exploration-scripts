import React, { useState, useEffect } from 'react';
import axios from "axios";
import SingleRowTable from '../../graph/table/SingleRowTable';
const columns = [
    { Header: 'Machine Name', accessor: 'machine' },
    { Header: 'Model Name', accessor: 'model_name' },
    { Header: 'Architecture', accessor: 'architecture' },
    { Header: 'Number of cores', accessor: 'num_cores' },
    { Header: 'Frequency Driver', accessor: 'freq_driver' },
    { Header: 'Frequency Governer', accessor: 'freq_governor' },
    { Header: 'Huge Page', accessor: 'huge_page' },
    { Header: 'Number of Sockets', accessor: 'num_sockets' },
    { Header: 'Number of Cores per Socket', accessor: 'num_core_per_socket' },


];


export default function SystemConfig() {

    const [tableData, setTableData] = useState([]);
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_system_config_data`)
            .then((response) => {

                const rawData = response.data

                setTableData(rawData);



            })

    }, [])


    return (
        <div className="textPageContainer">
            <h1>System Config Page</h1>

            {
                Object.entries(tableData).map(([architectureKey, architectureValue]) => (
                    <div key={architectureKey}>
                        <h2>{architectureKey}</h2>
                        <SingleRowTable
                            columns={columns}
                            data={[architectureValue]}
                        />
                    </div>
                ))
            }

        </div>
    );


}