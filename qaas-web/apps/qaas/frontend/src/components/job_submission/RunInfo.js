import { updateState } from "./JobSubUtil";
import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import TableContainer from '@mui/material/TableContainer';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import DeleteIcon from '@mui/icons-material/RemoveCircleOutline';
import AddIcon from '@mui/icons-material/AddCircleOutline';
export const RunInfo = ({ input, setInput }) => {

    const handleDelete = (i) => {
        const oldEnv = input.application.RUN.APP_ENV_MAP;
        const deletedEnv = oldEnv.filter((_, index) => index !== i);
        updateState(setInput, ['application', 'RUN', 'APP_ENV_MAP'], deletedEnv);

    };
    const handleCreate = () => {
        const oldEnv = input.application.RUN.APP_ENV_MAP;
        const newEnv = [
            ...oldEnv,
            { id: oldEnv.length + 1, name: '', value: '' },
        ];
        updateState(setInput, ['application', 'RUN', 'APP_ENV_MAP'], newEnv);

        // setEdit(true)
    };
    const handleUpdateEnv = (index, field, value) => {
        const newEnvVars = [...input.application.RUN.APP_ENV_MAP];
        const updatedVar = { ...newEnvVars[index], [field]: value };
        newEnvVars[index] = updatedVar;

        handleChange(['application', 'RUN', 'APP_ENV_MAP'], newEnvVars);
    };

    const handleChange = (path, value) => {
        updateState(setInput, path, value);
    };

    return (
        <div className="centeredBox">
            <div className="infoContent">
                <div className="infoTitle">Run</div>

                <div >
                    <div className="infoSubTitle">Data URL</div>
                    <TextField sx={{ width: '55ch' }} label="Data URL" variant="outlined"
                        onChange={e => handleChange(['application', 'GIT', 'DATA_URL'], e.target.value)}

                    />
                    <TextField id="outlined-basic" label="Data Branch" variant="outlined"
                        onChange={e => handleChange(['application', 'GIT', 'DATA_BRANCH'], e.target.value)}


                    />
                    <div>
                        <TextField label="Data User" id="outlined-basic" variant="outlined"
                            onChange={e => handleChange(['application', 'GIT', 'DATA_USER'], e.target.value)}


                        />
                        <TextField label="Data Token" id="outlined-basic" variant="outlined"
                            onChange={e => handleChange(['application', 'GIT', 'DATA_TOKEN'], e.target.value)}


                        />
                    </div>
                    <div>
                        <TextField fullWidth label="Data Download Path" id="outlined-basic" variant="outlined"
                            onChange={e => handleChange(['application', 'GIT', 'DATA_DOWNLOAD_PATH'], e.target.value)}


                        />
                    </div>
                    <div>
                        <div className="infoSubTitle">APP Run Command</div>
                        <TextField defaultValue={input.application.RUN.APP_RUN_CMD} fullWidth label="Data Download Path" id="outlined-basic" variant="outlined"

                            onChange={e => handleChange(['application', 'RUN', 'APP_RUN_CMD'], e.target.value)}

                        />
                    </div>
                    <div>

                        <div className="infoSubTitle">App scalability</div>
                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={input.application.RUN.APP_SCALABILITY_TYPE}
                            onChange={e => handleChange(['application', 'RUN', 'APP_SCALABILITY_TYPE'], e.target.value)}

                        >
                            <FormControlLabel value="Strong/Sequential" control={<Radio />} label="Strong/Sequential" />
                            <FormControlLabel value="Weak" control={<Radio />} label="Weak" />
                        </RadioGroup>
                    </div>
                </div>
                <div >
                    <div className="infoSubTitle">Env Variables</div>
                    <div >
                        <TableContainer component={Paper}>
                            <Table aria-label="simple table">
                                <TableHead>
                                    <TableRow>
                                        <TableCell align="center">Name</TableCell>
                                        <TableCell align="center">Value</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {input.application.RUN.APP_ENV_MAP.map((row, i) => (
                                        <TableRow>
                                            <TableCell contentEditable='true' align="center" onBlur={(e) => handleUpdateEnv(i, 'name', e.target.innerText)}>
                                                {row.name}
                                            </TableCell>
                                            <TableCell contentEditable='true' align="center" onBlur={(e) => handleUpdateEnv(i, 'value', e.target.innerText)}>

                                                {row.value}
                                            </TableCell>
                                            <TableCell align="center"><DeleteIcon onClick={() => handleDelete(i)} /></TableCell>


                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                        <AddIcon onClick={() => handleCreate()} />
                    </div>

                </div>
            </div>

        </div>
    );
};
