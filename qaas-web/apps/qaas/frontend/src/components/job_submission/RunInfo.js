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
import SettingsSelector from "./SettingSelector";
import SaveSettingButton from "./SaveSettingButton";
import { OPTIONAL_BLOCK_THEME } from "./JobSubUtil";
import { ThemeProvider } from '@mui/material/styles';

export const RunInfo = ({ input, setInput }) => {

    const handleDelete = (key) => {
        const oldEnv = { ...input.application.RUN.APP_ENV_MAP };
        delete oldEnv[key];
        updateState(setInput, ['application', 'RUN', 'APP_ENV_MAP'], oldEnv);
    };
    const handleCreate = () => {
        const key = `newKey${Object.keys(input.application.RUN.APP_ENV_MAP).length + 1}`;
        const newEnv = {
            ...input.application.RUN.APP_ENV_MAP,
            [key]: '',
        };
        updateState(setInput, ['application', 'RUN', 'APP_ENV_MAP'], newEnv);
    };
    const handleUpdateKey = (oldKey, newKey) => {
        const { [oldKey]: oldValue, ...rest } = input.application.RUN.APP_ENV_MAP;
        const newEnv = { ...rest, [newKey]: oldValue };

        updateState(setInput, ['application', 'RUN', 'APP_ENV_MAP'], newEnv);
    };

    const handleUpdateValue = (key, newValue) => {
        const newEnv = { ...input.application.RUN.APP_ENV_MAP, [key]: newValue };

        updateState(setInput, ['application', 'RUN', 'APP_ENV_MAP'], newEnv);
    };


    const handleChange = (path, value) => {
        updateState(setInput, path, value);
    };

    return (
        <div className="centeredBox">
            <div className="infoContent">

                <div className="headerContainer" >
                    <div className="infoTitle">Run Info</div>
                    <div className="settingSelector">
                        <SaveSettingButton input={input} />
                        <SettingsSelector setInput={setInput} />
                    </div>

                </div>

                <div >
                    <div className="block">
                        <div>
                            <div className="infoSubTitle">Run Command</div>
                            <TextField defaultValue={input.application.RUN.APP_RUN_CMD} fullWidth label="Run Command" id="outlined-basic" variant="outlined"

                                onChange={e => handleChange(['application', 'RUN', 'APP_RUN_CMD'], e.target.value)}
                                value={input.application.RUN.APP_RUN_CMD}


                            />
                        </div>
                    </div>
                    <ThemeProvider theme={OPTIONAL_BLOCK_THEME}>

                        <div className="block optional-block">
                            <div className="blockTitle">Optional</div>

                            <div className="infoSubTitle">Data URL</div>

                            <TextField sx={{ width: '55ch' }} label="Data URL" variant="outlined"
                                onChange={e => handleChange(['application', 'GIT', 'DATA_URL'], e.target.value)}
                                value={input.application.GIT.DATA_URL}


                            />

                            <TextField id="outlined-basic" label="Data Branch" variant="outlined"
                                onChange={e => handleChange(['application', 'GIT', 'BRANCH'], e.target.value)}
                                value={input.application.GIT.BRANCH}


                            />
                            <div>
                                <TextField label="Data User" id="outlined-basic" variant="outlined"
                                    onChange={e => handleChange(['application', 'GIT', 'DATA_USER'], e.target.value)}

                                    value={input.application.GIT.DATA_USER}

                                />

                                <TextField label="Data Password" id="outlined-password-input" variant="outlined" type="password"
                                    onChange={e => handleChange(['application', 'GIT', 'DATA_TOKEN'], e.target.value)}

                                    value={input.application.GIT.DATA_TOKEN}

                                />
                            </div>
                            <div>
                                <TextField fullWidth label="Data File Location" id="outlined-basic" variant="outlined"
                                    onChange={e => handleChange(['application', 'GIT', 'DATA_DOWNLOAD_PATH'], e.target.value)}
                                    value={input.application.GIT.DATA_DOWNLOAD_PATH}


                                />
                            </div>

                            <div>

                                <div className="infoSubTitle">MPI</div>
                                <RadioGroup
                                    row
                                    aria-labelledby="demo-row-radio-buttons-group-label"
                                    name="row-radio-buttons-group"
                                    defaultValue={input.runtime.MPI}
                                    onChange={e => handleChange(['runtime', 'MPI'], e.target.value)}

                                >
                                    <FormControlLabel value="no" control={<Radio />} label="No (Default)" />
                                    <FormControlLabel value="yes" control={<Radio />} label="Yes" />
                                    <FormControlLabel value="strong" control={<Radio />} label="Strong" />
                                    <FormControlLabel value="weak" control={<Radio />} label="Weak" />
                                </RadioGroup>
                            </div>
                            <div>

                                <div className="infoSubTitle">OPENMP</div>
                                <RadioGroup
                                    row
                                    aria-labelledby="demo-row-radio-buttons-group-label"
                                    name="row-radio-buttons-group"
                                    defaultValue={input.runtime.OPENMP}
                                    onChange={e => handleChange(['runtime', 'OPENMP'], e.target.value)}

                                >
                                    <FormControlLabel value="strong" control={<Radio />} label="Strong (Default)" />
                                    <FormControlLabel value="weak" control={<Radio />} label="Weak" />
                                </RadioGroup>
                            </div>
                            <div >
                                <div className="infoSubTitle">Env Variables</div>
                                <div >
                                    <div className="env-table ">
                                        <TableContainer component={Paper}>
                                            <Table aria-label="simple table">
                                                {/* only show table header when there is env variables */}
                                                {Object.entries(input.application.RUN.APP_ENV_MAP).length > 0 && (

                                                    <TableHead>
                                                        <TableRow>
                                                            <TableCell align="center">Name</TableCell>
                                                            <TableCell align="center">Value</TableCell>
                                                        </TableRow>
                                                    </TableHead>
                                                )}
                                                <TableBody>
                                                    {Object.entries(input.application.RUN.APP_ENV_MAP).map(([key, value]) => (
                                                        <TableRow key={key}>
                                                            <TableCell align="center">
                                                                <TextField
                                                                    fullWidth
                                                                    defaultValue={key}
                                                                    onBlur={(e) => handleUpdateKey(key, e.target.value)}
                                                                />
                                                            </TableCell>
                                                            <TableCell align="center">
                                                                <TextField
                                                                    fullWidth
                                                                    defaultValue={value}
                                                                    onBlur={(e) => handleUpdateValue(value, e.target.value)}
                                                                />
                                                            </TableCell>
                                                            <TableCell align="center">
                                                                <DeleteIcon onClick={() => handleDelete(key)} />
                                                            </TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>
                                    </div>
                                    <AddIcon onClick={() => handleCreate()} />

                                </div>

                            </div>
                        </div>
                    </ThemeProvider>

                </div>

            </div>

        </div>
    );
};
