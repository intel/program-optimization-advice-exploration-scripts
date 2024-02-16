import { updateState, validateField } from "./JobSubUtil";
import React, { useState, useEffect } from 'react';
import TextField from '@mui/material/TextField';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
export const BuildInfo = ({ input, setInput }) => {

    const [errors, setErrors] = useState({});



    const handleChange = (path, value) => {
        const field = path[path.length - 1];
        const error = validateField(value, field);
        setErrors((prevErrors) => ({ ...prevErrors, [field]: error }));
        if (!error) {
            updateState(setInput, path, value);
        }
    };

    return (
        <div className="centeredBox" >
            <div className="infoContent">


                <div className="infoTitle">Build</div>
                <div >
                    <div className="infoSubTitle">App Name</div>
                    <TextField label="App Name" variant="outlined" required
                        onChange={e => handleChange(['application', 'APP_NAME'], e.target.value)}
                        error={!!errors.APP_NAME}
                        helperText={errors.APP_NAME || ''}

                    />
                    <div className="infoSubTitle">Source tarball URL</div>
                    <TextField sx={{ width: '55ch' }} label="git location" variant="outlined"
                        onChange={(event) => handleChange(['application', 'GIT', 'SRC_URL'], event.target.value)}

                    />
                    <TextField id="outlined-basic" label="branch" variant="outlined"
                        onChange={(event) => handleChange(['application', 'GIT', 'BRANCH'], event.target.value)}

                    />
                    <div>
                        <TextField label="Git User" id="outlined-basic" variant="outlined"
                            onChange={(event) => handleChange(['application', 'GIT', 'USER'], event.target.value)}
                            error={!!errors.USER}
                            helperText={errors.USER || ''}


                        />
                        <TextField label="Git Token" id="outlined-basic" variant="outlined"
                            onChange={(event) => handleChange(['application', 'GIT', 'TOKEN'], event.target.value)}

                        />
                    </div>

                </div>
                <div >
                    <div className="infoSubTitle">Compiler and Flags</div>
                    <div>
                        <FormControl sx={{ minWidth: 120 }}>
                            <InputLabel id="demo-simple-select-label">Compiler</InputLabel>
                            <Select
                                labelId="demo-simple-select-label"
                                id="demo-simple-select"
                                value={input.compiler.USER_CC}
                                label="Compiler"
                                onChange={(event) => handleChange(['compiler', 'USER_CC'], event.target.value)}

                            >
                                <MenuItem value={"icc"}>ICC</MenuItem>
                                <MenuItem value={"gcc"}>GCC</MenuItem>
                                <MenuItem value={"llvm"}>LLVM</MenuItem>
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
                            </Select>
                        </FormControl>


                    </div>
                    <TextField label="CFLAGS" id="outlined-basic" variant="outlined"
                        onChange={(event) => handleChange(['compiler', 'USER_C_FLAGS'], event.target.value)}


                    />
                    <TextField id="outlined-basic" label="CXXFLAGS" variant="outlined"
                        onChange={(event) => handleChange(['compiler', 'USER_CXX_FLAGS'], event.target.value)}


                    />
                    <TextField id="outlined-basic" label="FCFLAGS" variant="outlined"
                        onChange={(event) => handleChange(['compiler', 'USER_FC_FLAGS'], event.target.value)}

                    />
                    <TextField id="outlined-basic" label="Link Flags" variant="outlined"
                        onChange={(event) => handleChange(['compiler', 'USER_LINK_FLAGS'], event.target.value)}


                    />

                </div>

                <div >
                    <div className="infoSubTitle">Libraries</div>
                    <div>
                        <FormControl sx={{ minWidth: 160 }}>
                            <InputLabel id="demo-simple-select-label">Math Libraries</InputLabel>
                            <Select
                                labelId="demo-simple-select-label"
                                id="demo-simple-select"
                                value={input.library.USER_MATH}
                                label="Math Libraries"
                                onChange={(event) => handleChange(['library', 'USER_MATH'], event.target.value)}

                            >
                                <MenuItem value={"Intel MKL"}>Intel MKL</MenuItem>
                                <MenuItem value={"OpenBLAS"}>OpenBLAS</MenuItem>
                                <MenuItem value={"GNU Scientific"}>GNU Scientific</MenuItem>
                            </Select>

                        </FormControl>
                        <FormControl sx={{ minWidth: 160 }}>
                            <InputLabel id="demo-simple-select-label">MPI Libraries</InputLabel>
                            <Select
                                labelId="demo-simple-select-label"
                                id="demo-simple-select"
                                value={input.library.USER_MPI}
                                label="MPI Libraries"
                                onChange={(event) => handleChange(['library', 'USER_MPI'], event.target.value)}

                            >
                                <MenuItem value={"Intel MPI"}>Intel MPI</MenuItem>
                                <MenuItem value={"Open MPI"}>Open MPI</MenuItem>
                                <MenuItem value={"OPAL MPI"}>OPAL MPI</MenuItem>
                            </Select>
                        </FormControl>

                    </div>
                </div>
                <div >
                    <div className="infoSubTitle">Target Binary Location</div>
                    <TextField sx={{ pr: '5px' }} id="outlined-basic" label="User Target" variant="outlined"
                        onChange={(event) => handleChange(['compiler', 'USER_TARGET'], event.target.value)}
                    />
                    <TextField sx={{ width: '55ch' }} id="outlined-basic" label="User Target Location" variant="outlined"

                        onChange={(event) => handleChange(['compiler', 'USER_TARGET_LOCATION'], event.target.value)}

                    />
                </div>

            </div>
        </div>
    );
};
