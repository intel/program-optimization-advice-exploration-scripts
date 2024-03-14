import { updateState, validateField } from "./JobSubUtil";
import React, { useState, useEffect } from 'react';
import TextField from '@mui/material/TextField';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import SettingsSelector from "./SettingSelector";
import SaveSettingButton from "./SaveSettingButton";
import { OPTIONAL_BLOCK_THEME } from "./JobSubUtil";
import { ThemeProvider } from '@mui/material/styles';

export const BuildInfo = ({ input, setInput, errors, updateFormErrors }) => {




    const handleChange = (path, value) => {
        const field = path[path.length - 1];
        updateState(setInput, path, value);

        const error = validateField(value, field);
        updateFormErrors(field, error);



    };


    return (
        <div className="centeredBox" >
            <div className="infoContent">


                <div className="headerContainer" >
                    <div className="infoTitle">Build Info</div>
                    <div className="settingSelector">
                        <SaveSettingButton input={input} />
                        <SettingsSelector setInput={setInput} />
                    </div>


                </div>
                <div className="block">
                    <div >
                        <div className="infoSubTitle">App Name</div>
                        <TextField label="App Name" variant="outlined"
                            onChange={e => handleChange(['application', 'APP_NAME'], e.target.value)}
                            error={!!errors.APP_NAME}
                            helperText={errors.APP_NAME || ''}
                            value={input.application.APP_NAME} />
                        <div className="infoSubTitle">Source tarball URL</div>
                        <TextField sx={{ width: '55ch' }} label="git location" variant="outlined"
                            onChange={(event) => handleChange(['application', 'GIT', 'SRC_URL'], event.target.value)}
                            value={input.application.GIT.SRC_URL} />
                        <TextField id="outlined-basic" label="branch" variant="outlined"
                            onChange={(event) => handleChange(['application', 'GIT', 'BRANCH'], event.target.value)}
                            value={input.application.GIT.BRANCH} />
                        <div>
                            <TextField label="Git User" id="outlined-basic" variant="outlined"
                                onChange={(event) => handleChange(['application', 'GIT', 'USER'], event.target.value)}
                                error={!!errors.USER}
                                helperText={errors.USER || ''}
                                value={input.application.GIT.USER} />
                            <TextField label="Git Password" id="outlined-basic" variant="outlined"
                                onChange={(event) => handleChange(['application', 'GIT', 'TOKEN'], event.target.value)}
                                value={input.application.GIT.TOKEN} />
                        </div>

                    </div>
                    <div >
                        <div className="infoSubTitle">Target Binary Location</div>
                        <TextField sx={{ pr: '5px' }} id="outlined-basic" label="Build Target" variant="outlined"
                            onChange={(event) => handleChange(['compiler', 'USER_TARGET'], event.target.value)}
                            value={input.compiler.USER_TARGET} />
                        <TextField sx={{ width: '55ch' }} id="outlined-basic" label="Build Target Location" variant="outlined"
                            onChange={(event) => handleChange(['compiler', 'USER_TARGET_LOCATION'], event.target.value)}
                            value={input.compiler.USER_TARGET_LOCATION} />
                    </div>
                </div>
                <ThemeProvider theme={OPTIONAL_BLOCK_THEME}>

                    <div className="block optional-block">
                        <div className="blockTitle">Optional</div>

                        <div >
                            <div className="infoSubTitle">Default Compiler and Flags</div>
                            <div>
                                <FormControl sx={{ minWidth: 120 }}>
                                    <InputLabel id="demo-simple-select-label">Compiler</InputLabel>
                                    <Select
                                        labelId="demo-simple-select-label"
                                        id="demo-simple-select"
                                        value={input.compiler.USER_CC}
                                        label="Compiler"
                                        onChange={(event) => handleChange(['compiler', 'USER_CC'], event.target.value)}>
                                        <MenuItem value={"icc"}>ICC</MenuItem>
                                        <MenuItem value={"gcc"}>GCC</MenuItem>
                                        <MenuItem value={"llvm"}>LLVM</MenuItem>
                                        <MenuItem value={"mpiicc-icx"}>mpiicc-icx</MenuItem>
                                    </Select>

                                </FormControl>
                                <FormControl sx={{ minWidth: 120 }}>
                                    <InputLabel id="demo-simple-select-label">Version</InputLabel>
                                    <Select
                                        labelId="demo-simple-select-label"
                                        id="demo-simple-select"
                                        value={input.compiler.USER_CC_VERSION}
                                        label="Version"
                                        onChange={(event) => handleChange(['compiler', 'USER_CC_VERSION'], event.target.value)}

                                    >
                                        <MenuItem value={"2022"}>2022</MenuItem>
                                        <MenuItem value={"2023"}>2023</MenuItem>

                                    </Select>
                                </FormControl>


                            </div>
                            <TextField label="CFLAGS" id="outlined-basic" variant="outlined"
                                onChange={(event) => handleChange(['compiler', 'USER_C_FLAGS'], event.target.value)}
                                value={input.compiler.USER_C_FLAGS} />
                            <TextField id="outlined-basic" label="CXXFLAGS" variant="outlined"
                                onChange={(event) => handleChange(['compiler', 'USER_CXX_FLAGS'], event.target.value)}
                                value={input.compiler.USER_CXX_FLAGS} />
                            <TextField id="outlined-basic" label="FCFLAGS" variant="outlined"
                                onChange={(event) => handleChange(['compiler', 'USER_FC_FLAGS'], event.target.value)}
                                value={input.compiler.USER_FC_FLAGS} />
                            <TextField id="outlined-basic" label="Link Flags" variant="outlined"
                                onChange={(event) => handleChange(['compiler', 'USER_LINK_FLAGS'], event.target.value)}
                                value={input.compiler.USER_LINK_FLAGS} />

                        </div>

                    </div>
                </ThemeProvider>

            </div>
        </div>
    );
};
