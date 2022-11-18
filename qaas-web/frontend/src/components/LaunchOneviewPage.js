import React, { useState, useEffect } from 'react';
import axios from "axios";

import LoadingAlert from "./LoadingAlert";
// import DataTable from "./graph/DataTable";
import UserInput from './UserInput';
import Button from '@mui/material/Button';
// import StatusPanel from './StatusPanel';
export default function LaunchOneviewPage() {
    // const [timestamps, setTimestamps] = useState([]);
    // const [isLoading, setIsLoading] = useState(false);
    // const [isRunning, setIsRunning] = useState(false);
    // const [shouldShowLoading, setShouldShowLoading] = useState(false);

    useEffect(() => {
        // setIsLoading(true)
        axios.get("/get_all_timestamps")
            .then((response) => {
                // setTimestamps(JSON.parse(response.data['timestamps']))
                // setIsLoading(false)
            })

    }, [])

  
    const handleLaunchRunClick = (e) => {
        // setIsRunning(true)
        // setShouldShowLoading(true)
        axios.post("/create_new_timestamp", {})
            .then((response) => {
                // setTimestamps(preState => [
                //     ...preState,
                //     response.data['timestamp']
                // ])
                // setIsRunning(false)
                // setShouldShowLoading(false)
                console.log(JSON.parse(response.data['timestamp']))
            })

    }

    return (
        <div style={{marginTop:80}}>
            <UserInput/>
            <Button  variant="contained" type="button" onClick={() => handleLaunchRunClick()}>Launch run button</Button >
            
            {/* {isRunning && shouldShowLoading && <LoadingAlert text="Running..." />} */}

            {/* {timestamps.length > 0 && <DataTable columns_raw={["timestamps"]} rows_raw={timestamps} />}
            <div style={{"height":"400px"}}></div>


            {isLoading && !isRunning && shouldShowLoading && <LoadingAlert text="Loading..." />} */}
            {/* <div>{!isLoading && !isRunning && shouldLoadHTML && <div ><Iframe id="html" className="htmlclass" url={filepath} height="1000px" width="100%" /></div>}</div> */}
        </div>

    );
}
