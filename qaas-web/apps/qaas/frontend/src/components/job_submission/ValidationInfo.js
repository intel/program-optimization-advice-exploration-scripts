import { updateState } from "./JobSubUtil";
import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';


export const ValidationInfo = ({ input, setInput }) => {

    const titleStyle = {
        fontSize: '1.5em',
        fontWeight: 'bold'
    };

    const divStyle = {
        padding: '5px'
    };


    return (
        <div className="centeredBox">
            <div className="infoContent">

                <div style={titleStyle}>Validation and Domain Specific Rate</div>

                <div style={divStyle}>
                    <div className="infoSubTitle">Validation Script URL</div>
                    <TextField sx={{ width: '55ch', pr: '5px' }} label="Validation Script URL" variant="outlined"
                        onChange={e => handleChange(['application', 'GIT', 'DATA_URL'], e.target.value)}


                    />
                    <TextField id="outlined-basic" label="Validation Script Branch" variant="outlined"
                        onChange={e => handleChange(['application', 'GIT', 'DATA_BRANCH'], e.target.value)}


                    />
                    <div>
                        <TextField sx={{ pr: '5px', pt: '5px' }} label="Validation Script User" id="outlined-basic" variant="outlined"
                            onChange={e => handleChange(['application', 'GIT', 'DATA_USER'], e.target.value)}


                        />
                        <TextField sx={{ pr: '5px', pt: '5px' }} label="Validation Script Token" id="outlined-basic" variant="outlined"
                            onChange={e => handleChange(['application', 'GIT', 'DATA_TOKEN'], e.target.value)}


                        />
                    </div>
                    <div>
                        <TextField fullWidth sx={{ pr: '5px', pt: '5px' }} label="Validation Script Download Path" id="outlined-basic" variant="outlined"
                            onChange={e => handleChange(['application', 'GIT', 'DATA_DOWNLOAD_PATH'], e.target.value)}


                        />
                    </div>
                </div>
                <div style={divStyle}>
                    <div className="infoSubTitle">Rate Script URL</div>
                    <TextField sx={{ width: '55ch', pr: '5px' }} label="Rate Script URL" variant="outlined"
                        onChange={e => handleChange(['application', 'GIT', 'DATA_URL'], e.target.value)}


                    />
                    <TextField id="outlined-basic" label="Rate Script Branch" variant="outlined"
                        onChange={e => handleChange(['application', 'GIT', 'DATA_BRANCH'], e.target.value)}


                    />
                    <div>
                        <TextField sx={{ pr: '5px', pt: '5px' }} label="Rate Script User" id="outlined-basic" variant="outlined"
                            onChange={e => handleChange(['application', 'GIT', 'DATA_USER'], e.target.value)}


                        />
                        <TextField sx={{ pr: '5px', pt: '5px' }} label="Rate Script Token" id="outlined-basic" variant="outlined"
                            onChange={e => handleChange(['application', 'GIT', 'DATA_TOKEN'], e.target.value)}


                        />
                    </div>
                    <div>
                        <TextField fullWidth sx={{ pr: '5px', pt: '5px' }} label="Rate Script Download Path" id="outlined-basic" variant="outlined"
                            onChange={e => handleChange(['application', 'GIT', 'DATA_DOWNLOAD_PATH'], e.target.value)}


                        />
                    </div>
                </div>
            </div>
        </div>
    );
};
