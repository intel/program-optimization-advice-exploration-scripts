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
    const envRows = [
        { id: 1, name: 'name1', value: 'value1' },
    ];
    const [envrows, setEnvRows] = useState(envRows);
    const handleDelete = (i) => {
        setEnvRows((prevEnvRows) =>
            prevEnvRows.filter((_, index) => index !== i)
        );
    };
    const handleCreate = () => {
        setEnvRows(prevEnvRows => [
            ...prevEnvRows,
            { id: prevEnvRows.length + 1, name: '', value: '' }
        ])
        // setEdit(true)
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
                                    {envrows.map((row, i) => (
                                        <TableRow>
                                            <TableCell contentEditable='true' align="center">{row.name}</TableCell>
                                            <TableCell contentEditable='true' align="center">{row.value}</TableCell>
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
