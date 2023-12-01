import React, { useState, useEffect } from "react";
import { DataGrid } from '@mui/x-data-grid';
import axios from "axios";
import Iframe from 'react-iframe';
import LoadingAlert from "../LoadingAlert";
// function configColumns(column) {
//     return { field: column, headerName: column, width: 90 }
// }
function configRows(item, index) {
    var res = { "id": index + 1, "timestamps": item };
    // console.log("configrows", res)

    return res
}


export default function DataTable({ columns_raw, rows_raw, isLoading, shouldLoadHTML, setIsLoading, setShouldLoadHTML }) {
    //style
    const splitScreen = {
        display: 'flex',
        flexDirection: 'row',
        paddingBottom: "10px"
    }
    const leftPane = {
        width: '50%',

    }
    const rightPane = {
        width: '50%',
        paddingLeft: "10px"
    }
    //state
    const [neededInfo, setNeededInfo] = useState({});
    const [shouldShowLoading, setShouldShowLoading] = useState(false);
    const [loadTimestampTable, setLoadTimeStampTable] = useState(false);

    const columns = [{ field: 'id', headerName: 'ID', width: 90 },
    { field: columns_raw[0], headerName: columns_raw[0], width: 200 }]
    const rows = rows_raw.map(configRows)
    useEffect(() => {
        axios.post("/get_data_table_rows", {})
            .then((response) => {
                setNeededInfo(JSON.parse(response.data['data']))
            })

    }, [])
    const main_table_columns = [
        { field: 'id', headerName: 'ID', width: 90 },
        { field: "Application", headerName: "Application", width: 200 },
        { field: "Machine", headerName: "Machine", width: 200 },
        { field: "Dataset", headerName: "Dataset", width: 200 }
    ]
    const main_table_rows = [{ "id": 1, "Application": neededInfo["Application"], "Machine": neededInfo["Machine"], "Dataset": neededInfo["Dataset"] }]

    const handleEvent = () => {
        setLoadTimeStampTable(!loadTimestampTable);
    }
    const handleTimestampClick = (params) => {
        setIsLoading(true)
        setShouldShowLoading(true)
        setShouldLoadHTML(false)
        console.log("params is ", params['row']['timestamps'])
        axios.post("/get_html_by_timestamp", { timestamp: params['row']['timestamps'] })
            .then((response) => {
                setIsLoading(false)
                setShouldShowLoading(false)
                setShouldLoadHTML(true)
            })
    }
    var orig_filepath = process.env.PUBLIC_URL + '/orig/otter_html/index.html'
    var opt_filepath = process.env.PUBLIC_URL + '/opt/otter_html/index.html'
    console.log(isLoading, shouldLoadHTML)
    return (

        <div style={{ height: 400, width: '100%' }}>
            <DataGrid
                onCellClick={handleEvent}
                rows={main_table_rows}
                columns={main_table_columns}
                pageSize={5}
                rowsPerPageOptions={[5]}
                checkboxSelection
            />
            {loadTimestampTable && <DataGrid
                onCellClick={(params) => handleTimestampClick(params)}
                rows={rows}
                columns={columns}
                pageSize={5}
                rowsPerPageOptions={[5]}
                checkboxSelection
            />}
            {isLoading && shouldShowLoading && <LoadingAlert text="Loading..." />}
            {!isLoading && shouldLoadHTML &&

                <div style={splitScreen}>
                    <div style={leftPane}>

                        <div><div ><Iframe id="html" className="htmlclass" url={orig_filepath} height="1000px" width="100%" /></div></div>
                    </div>
                    <div style={rightPane}>

                        <div> <div ><Iframe id="html" className="htmlclass" url={opt_filepath} height="1000px" width="100%" /></div></div>
                    </div>
                </div>
            }

        </div>
    );
}
