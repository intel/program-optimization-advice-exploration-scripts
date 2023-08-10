import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Checkbox from '@mui/material/Checkbox';
import DeleteIcon from '@mui/icons-material/RemoveCircleOutline';
import AddIcon from '@mui/icons-material/AddCircleOutline';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import TextField from '@mui/material/TextField';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import StatusPanel from './StatusPanel';
import Button from '@mui/material/Button';
import axios from "axios";
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Typography from '@mui/material/Typography';
import { useNavigate } from 'react-router-dom'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';

const steps = ['Build Info', 'Run Info', 'Golden Run System Settings', 'Optional Run System Settings', 'Validation and Domain Specific Rate', 'Status Info'];

export default function UserInputStepper({ isLoading, shouldLoadHTML, setIsLoading, setShouldLoadHTML }) {
    const [activeStep, setActiveStep] = React.useState(0);
    const [skipped, setSkipped] = React.useState(new Set());

    const [statusMsg, setStatusMsg] = useState("");
    const isStepOptional = (step) => {
        return step === 4;
    };

    const isStepSkipped = (step) => {
        return skipped.has(step);
    };

    const handleNext = () => {
        let newSkipped = skipped;
        if (isStepSkipped(activeStep)) {
            newSkipped = new Set(newSkipped.values());
            newSkipped.delete(activeStep);
        }

        setActiveStep((prevActiveStep) => prevActiveStep + 1);
        setSkipped(newSkipped);
    };

    const handleSumbitNext = () => {
        let newSkipped = skipped;
        if (isStepSkipped(activeStep)) {
            newSkipped = new Set(newSkipped.values());
            newSkipped.delete(activeStep);
        }


        setActiveStep((prevActiveStep) => prevActiveStep + 1);
        setSkipped(newSkipped);

        //build connection stream
        const sse = new EventSource('http://localhost:5002/stream')

        function handleStream(e) {
            setStatusMsg(e.data)
        }
        sse.onopen = e => {
        }
        sse.onmessage = e => {
            handleStream(e)
        }
        sse.addEventListener('ping', e => {
            setStatusMsg(e.data)
        })
        sse.onerror = e => {
            //GOTCHA - can close stream and 'stall'
            sse.close()
        }


        //call backend
        setSSEStatus(true)
        axios.post("/create_new_timestamp", input)
            .then((response) => {
                setSSEStatus(false)
                return () => {
                    sse.close()

                }
            }
            )


    };


    const handleBack = () => {
        setActiveStep((prevActiveStep) => prevActiveStep - 1);
    };

    const handleSkip = () => {
        if (!isStepOptional(activeStep)) {
            // You probably want to guard against something like this,
            // it should never occur unless someone's actively trying to break something.
            throw new Error("You can't skip a step that isn't optional.");
        }

        setActiveStep((prevActiveStep) => prevActiveStep + 1);
        setSkipped((prevSkipped) => {
            const newSkipped = new Set(prevSkipped.values());
            newSkipped.add(activeStep);
            return newSkipped;
        });
    };

    const handleReset = () => {
        setActiveStep(0);
    };



    /******************************************************************* Written Prepare Code *************************************************/
    const divStyle = {
        padding: '5px'
    }
    const titleStyle = {
        fontSize: '1.5em',
        fontWeight: 'bold'
    }
    const subtitleStyle = {
        fontSize: '1.2em',

    }
    const envTableStyle = {
        height: 400,
        width: '100%'
    }

    const navigate = useNavigate();
    const envRows = [
        { id: 1, name: 'name1', value: 'value1' },
        { id: 2, name: 'name2', value: 'value2' },
    ];

    //state
    const [envrows, setEnvRows] = useState(envRows);
    //socket
    const [SSEStatus, setSSEStatus] = useState(false);
    //default checked

    //user input state
    //input state
    const [input, setInput] = useState(
        {
            account: {
                QAAS_ACCOUNT: "intel"
            },
            application: {
                APP_NAME: "",
                GIT: {
                    USER: "",
                    TOKEN: "",
                    BRANCH: "",
                    SRC_URL: "",
                    DATA_USER: "",
                    DATA_TOKEN: "",
                    DATA_URL: "",
                    DATA_BRANCH: "",
                    DATA_DOWNLOAD_PATH: ""
                },
                RUN: {
                    APP_DATA_ARGS: "",
                    APP_RUN_CMD: "<binary>",
                    APP_ENV_MAP: {},
                    APP_SCALABILITY_TYPE: "Strong/Sequential"
                }
            },
            compiler: {
                USER_CC: "icc",
                USER_CC_VERSION: "2022",
                USER_C_FLAGS: "",
                USER_CXX_FLAGS: "",
                USER_FC_FLAGS: "",
                USER_LINK_FLAGS: "",
                USER_TARGET: "",
                USER_TARGET_LOCATION: ""
            },
            library: {
                USER_MPI: "Intel MPI",
                USER_MATH: "Intel MKL"
            },
            system: {
                USER_OPTION: {
                    CPU: "",
                    HYPERTHREADING: "",
                    HUGEPAGE: "",
                    TURBO_BOOST: "",
                    FREQ_SCALING: "",
                    PREFETCH: "",
                },
                SEARCH_OPTIONS: {
                    CPU: ["Default"],
                    HYPERTHREADING: ["Default"],
                    HUGEPAGE: ["Default"],
                    TURBO_BOOST: ["Default"],
                    FREQ_SCALING: ["Default"],
                    PREFETCH: ["Default"],
                    COMPILER: ["Default"]
                }

            }
        }
    )

    const handleFinishButtonClick = () => {
        setIsLoading(false)
        setShouldLoadHTML(true)
        navigate('/result')
    };
    const isValueInInput = (input_location, value) => {
        return input_location.indexOf[value] > -1
    }
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
    const handleCheckBoxClick = (e, default_button_name) => {
        //set component to checked
        //delete default from input
        //add component to input
        const s = { ...input }
        var filteredArray = s.system.SEARCH_OPTIONS.filter(function (e) { return e !== default_button_name })
        setInput({ ...s })
    }
    //constant sub components
    const checkBoxComponent = ({ title, listItems }) => {
        return (
            <div >
                {title}

                <div>
                    {listItems.map((item, index) => {

                    })}
                    Skylake <Checkbox checked={isValueInInput(input.system.SEARCH_OPTIONS.CPU, "Skylake")} onChange={(e) => handleCheckBoxClick(e, "cpu")} />
                    Cascadelake <Checkbox checked={input.system.SEARCH_OPTIONS.CPU.indexOf("Cascadelake") > -1} onChange={(e) => handleCheckBoxClick(e, "cpu")} />
                    Ice Lake <Checkbox checked={input.system.SEARCH_OPTIONS.CPU.indexOf("Ice Lake") > -1} onChange={(e) => handleCheckBoxClick(e, "cpu")} />
                    Default <Checkbox defaultChecked />
                </div>
            </div>

        )
    }



    /******************************************************************* Finish prepare Written Code *************************************************/

    return (
        <div >
            <Box sx={{ marginTop: '80px', width: '100%' }}>
                <Stepper activeStep={activeStep}>
                    {steps.map((label, index) => {
                        const stepProps = {};
                        const labelProps = {};
                        if (isStepOptional(index)) {
                            labelProps.optional = (
                                <Typography variant="caption">Optional</Typography>
                            );
                        }
                        if (isStepSkipped(index)) {
                            stepProps.completed = false;
                        }
                        return (
                            <Step key={label} {...stepProps}>
                                <StepLabel {...labelProps}>{label}</StepLabel>
                            </Step>
                        );
                    })}
                </Stepper>
                {activeStep === steps.length ? (
                    <React.Fragment>
                        <Typography sx={{ mt: 2, mb: 1 }}>
                            All steps completed - you&apos;re finished
                        </Typography>
                        <Button sx={{ ml: 3 }} variant="contained" onClick={handleFinishButtonClick} endIcon={<ArrowForwardIcon />}>See Result</Button>

                        <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
                            <Box sx={{ flex: '1 1 auto' }} />
                            <Button onClick={handleReset}>Reset</Button>
                        </Box>
                    </React.Fragment>
                ) : (
                    <React.Fragment>
                        <Typography sx={{ mt: 2, mb: 1 }}>Step {activeStep + 1}</Typography>

                        {activeStep === 0 &&

                            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }} >
                                <Box

                                    sx={{
                                        padding: '20px',
                                        width: '70%',
                                        boxShadow: 3

                                    }}
                                >

                                    <div style={titleStyle}>Build</div>
                                    <div style={divStyle}>
                                        <div style={subtitleStyle}>App Name</div>
                                        <TextField sx={{ width: '55ch', pr: '5px' }} label="App Name" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.application.APP_NAME = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <div style={subtitleStyle}>Source tarball URL</div>
                                        <TextField sx={{ width: '55ch', pr: '5px' }} label="git location" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.application.GIT.SRC_URL = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <TextField id="outlined-basic" label="branch" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.application.GIT.BRANCH = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <div>
                                            <TextField sx={{ pr: '5px', pt: '5px' }} label="Git User" id="outlined-basic" variant="outlined"
                                                onChange={
                                                    (event) => {
                                                        const s = { ...input }
                                                        s.application.GIT.USER = event.target.value
                                                        setInput({ ...s })
                                                    }
                                                }
                                            />
                                            <TextField sx={{ pr: '5px', pt: '5px' }} label="Git Token" id="outlined-basic" variant="outlined"
                                                onChange={
                                                    (event) => {
                                                        const s = { ...input }
                                                        s.application.GIT.TOKEN = event.target.value
                                                        setInput({ ...s })
                                                    }
                                                }
                                            />
                                        </div>

                                    </div>
                                    <div style={divStyle}>
                                        <div style={subtitleStyle}>Compiler and Flags</div>
                                        <div>
                                            <FormControl sx={{ minWidth: 120 }}>
                                                <InputLabel id="demo-simple-select-label">Compiler</InputLabel>
                                                <Select
                                                    labelId="demo-simple-select-label"
                                                    id="demo-simple-select"
                                                    value={input.compiler.USER_CC}
                                                    label="Compiler"
                                                    onChange={
                                                        (event) => {
                                                            const s = { ...input }
                                                            s.compiler.USER_CC = event.target.value
                                                            setInput({ ...s })
                                                        }
                                                    }
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
                                                    onChange={
                                                        (event) => {
                                                            const s = { ...input }
                                                            s.compiler.USER_CC_VERSION = event.target.value
                                                            setInput({ ...s })
                                                        }
                                                    }
                                                >
                                                    <MenuItem value={"2022"}>2022</MenuItem>
                                                </Select>
                                            </FormControl>


                                        </div>
                                        <TextField sx={{ pr: '5px', pt: '5px' }} label="CFLAGS" id="outlined-basic" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.compiler.USER_C_FLAGS = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <TextField sx={{ pr: '5px', pt: '5px' }} id="outlined-basic" label="CXXFLAGS" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.compiler.USER_CXX_FLAGS = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <TextField sx={{ pr: '5px', pt: '5px' }} id="outlined-basic" label="FCFLAGS" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.compiler.USER_FC_FLAGS = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <TextField sx={{ pr: '5px', pt: '5px' }} id="outlined-basic" label="Link Flags" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.compiler.USER_LINK_FLAGS = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />

                                    </div>

                                    <div style={divStyle}>
                                        <div style={subtitleStyle}>Libraries</div>
                                        <div>
                                            <FormControl sx={{ minWidth: 160 }}>
                                                <InputLabel id="demo-simple-select-label">Math Libraries</InputLabel>
                                                <Select
                                                    labelId="demo-simple-select-label"
                                                    id="demo-simple-select"
                                                    value={input.library.USER_MATH}
                                                    label="Math Libraries"
                                                    onChange={
                                                        (event) => {
                                                            const s = { ...input }
                                                            s.library = event.target.value
                                                            setInput({ ...s })
                                                        }
                                                    }
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
                                                    onChange={
                                                        (event) => {
                                                            const s = { ...input }
                                                            s.library.USER_MPI = event.target.value
                                                            setInput({ ...s })
                                                        }
                                                    }
                                                >
                                                    <MenuItem value={"Intel MPI"}>Intel MPI</MenuItem>
                                                    <MenuItem value={"Open MPI"}>Open MPI</MenuItem>
                                                    <MenuItem value={"OPAL MPI"}>OPAL MPI</MenuItem>
                                                </Select>
                                            </FormControl>

                                        </div>
                                    </div>
                                    <div style={divStyle}>
                                        <div style={subtitleStyle}>Target Binary Location</div>
                                        <TextField sx={{ pr: '5px' }} id="outlined-basic" label="User Target" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.compiler.USER_TARGET = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <TextField sx={{ width: '55ch' }} id="outlined-basic" label="User Target Location" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.compiler.USER_TARGET_LOCATION = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                    </div>


                                </Box>
                            </div>


                        }


                        {activeStep === 1 &&

                            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '75vh' }} >
                                <Box

                                    sx={{
                                        padding: '20px',
                                        width: '70%',
                                        boxShadow: 3

                                    }}
                                >
                                    <div style={titleStyle}>Run</div>

                                    <div style={divStyle}>
                                        <div style={subtitleStyle}>Data URL</div>
                                        <TextField sx={{ width: '55ch', pr: '5px' }} label="Data URL" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.application.GIT.DATA_URL = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <TextField id="outlined-basic" label="Data Branch" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.application.GIT.DATA_BRANCH = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <div>
                                            <TextField sx={{ pr: '5px', pt: '5px' }} label="Data User" id="outlined-basic" variant="outlined"
                                                onChange={
                                                    (event) => {
                                                        const s = { ...input }
                                                        s.application.GIT.DATA_USER = event.target.value
                                                        setInput({ ...s })
                                                    }
                                                }
                                            />
                                            <TextField sx={{ pr: '5px', pt: '5px' }} label="Data Token" id="outlined-basic" variant="outlined"
                                                onChange={
                                                    (event) => {
                                                        const s = { ...input }
                                                        s.application.GIT.DATA_TOKEN = event.target.value
                                                        setInput({ ...s })
                                                    }
                                                }
                                            />
                                        </div>
                                        <div>
                                            <TextField fullWidth sx={{ pr: '5px', pt: '5px' }} label="Data Download Path" id="outlined-basic" variant="outlined"
                                                onChange={
                                                    (event) => {
                                                        const s = { ...input }
                                                        s.application.GIT.DATA_DOWNLOAD_PATH = event.target.value
                                                        setInput({ ...s })
                                                    }
                                                }
                                            />
                                        </div>
                                        <div>
                                            <div style={subtitleStyle}>APP Run Command</div>
                                            <TextField defaultValue={input.application.RUN.APP_RUN_CMD} fullWidth sx={{ pr: '5px', pt: '5px' }} label="Data Download Path" id="outlined-basic" variant="outlined"
                                                onChange={
                                                    (event) => {
                                                        const s = { ...input }
                                                        s.application.RUN.APP_RUN_CMD = event.target.value
                                                        setInput({ ...s })
                                                    }
                                                }
                                            />
                                        </div>
                                        <div>

                                            <div style={subtitleStyle}>App scalability</div>
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
                                    <div style={divStyle}>
                                        <div style={subtitleStyle}>Env Variables</div>
                                        <div style={envTableStyle}>
                                            <TableContainer component={Paper}>
                                                <Table sx={{ minWidth: 300 }} aria-label="simple table">
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
                                            {/* <AddIcon style={{ padding: '1px' }} onClick={() => handleCreate()} /> */}
                                        </div>

                                    </div>
                                </Box>

                            </div>



                        }
                        {activeStep === 4 &&

                            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }} >
                                <Box

                                    sx={{
                                        padding: '20px',
                                        width: '70%',
                                        boxShadow: 3

                                    }}

                                >

                                    <div style={titleStyle}>Validation and Domain Specific Rate</div>

                                    <div style={divStyle}>
                                        <div style={subtitleStyle}>Validation Script URL</div>
                                        <TextField sx={{ width: '55ch', pr: '5px' }} label="Validation Script URL" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.application.GIT.DATA_URL = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <TextField id="outlined-basic" label="Validation Script Branch" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.application.GIT.DATA_BRANCH = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <div>
                                            <TextField sx={{ pr: '5px', pt: '5px' }} label="Validation Script User" id="outlined-basic" variant="outlined"
                                                onChange={
                                                    (event) => {
                                                        const s = { ...input }
                                                        s.application.GIT.DATA_USER = event.target.value
                                                        setInput({ ...s })
                                                    }
                                                }
                                            />
                                            <TextField sx={{ pr: '5px', pt: '5px' }} label="Validation Script Token" id="outlined-basic" variant="outlined"
                                                onChange={
                                                    (event) => {
                                                        const s = { ...input }
                                                        s.application.GIT.DATA_TOKEN = event.target.value
                                                        setInput({ ...s })
                                                    }
                                                }
                                            />
                                        </div>
                                        <div>
                                            <TextField fullWidth sx={{ pr: '5px', pt: '5px' }} label="Validation Script Download Path" id="outlined-basic" variant="outlined"
                                                onChange={
                                                    (event) => {
                                                        const s = { ...input }
                                                        s.application.GIT.DATA_DOWNLOAD_PATH = event.target.value
                                                        setInput({ ...s })
                                                    }
                                                }
                                            />
                                        </div>
                                    </div>
                                    <div style={divStyle}>
                                        <div style={subtitleStyle}>Rate Script URL</div>
                                        <TextField sx={{ width: '55ch', pr: '5px' }} label="Rate Script URL" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.application.GIT.DATA_URL = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <TextField id="outlined-basic" label="Rate Script Branch" variant="outlined"
                                            onChange={
                                                (event) => {
                                                    const s = { ...input }
                                                    s.application.GIT.DATA_BRANCH = event.target.value
                                                    setInput({ ...s })
                                                }
                                            }
                                        />
                                        <div>
                                            <TextField sx={{ pr: '5px', pt: '5px' }} label="Rate Script User" id="outlined-basic" variant="outlined"
                                                onChange={
                                                    (event) => {
                                                        const s = { ...input }
                                                        s.application.GIT.DATA_USER = event.target.value
                                                        setInput({ ...s })
                                                    }
                                                }
                                            />
                                            <TextField sx={{ pr: '5px', pt: '5px' }} label="Rate Script Token" id="outlined-basic" variant="outlined"
                                                onChange={
                                                    (event) => {
                                                        const s = { ...input }
                                                        s.application.GIT.DATA_TOKEN = event.target.value
                                                        setInput({ ...s })
                                                    }
                                                }
                                            />
                                        </div>
                                        <div>
                                            <TextField fullWidth sx={{ pr: '5px', pt: '5px' }} label="Rate Script Download Path" id="outlined-basic" variant="outlined"
                                                onChange={
                                                    (event) => {
                                                        const s = { ...input }
                                                        s.application.GIT.DATA_DOWNLOAD_PATH = event.target.value
                                                        setInput({ ...s })
                                                    }
                                                }
                                            />
                                        </div>
                                    </div>
                                </Box>
                            </div>
                        }
                        {activeStep === 2 &&
                            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '75vh' }} >
                                <Box

                                    sx={{
                                        padding: '20px',
                                        width: '70%',
                                        boxShadow: 3

                                    }}
                                >
                                    <div style={divStyle}>
                                        <div style={titleStyle}>Golden Run System Settings</div>
                                        <div>
                                            CPU choices
                                            <RadioGroup
                                                row
                                                aria-labelledby="demo-row-radio-buttons-group-label"
                                                name="row-radio-buttons-group"
                                                defaultValue={"Default"}
                                            >
                                                <FormControlLabel value="Sky Lake" control={<Radio />} label="Sky Lake" />
                                                <FormControlLabel value="Cascade Lake" control={<Radio />} label="Cascade Lake" />
                                                <FormControlLabel value="Ice Lake" control={<Radio />} label="Ice Lake" />
                                                <FormControlLabel value="Default" control={<Radio />} label="Default" />
                                            </RadioGroup>
                                        </div>
                                        <div>
                                            Hyperthreading
                                            <RadioGroup
                                                row
                                                aria-labelledby="demo-row-radio-buttons-group-label"
                                                name="row-radio-buttons-group"
                                                defaultValue={"Default"}
                                            >
                                                <FormControlLabel value="on" control={<Radio />} label="ON" />
                                                <FormControlLabel value="off" control={<Radio />} label="OFF" />
                                                <FormControlLabel value="Default" control={<Radio />} label="Default" />
                                            </RadioGroup>
                                        </div>
                                        <div>
                                            Huge Page
                                            <RadioGroup
                                                row
                                                aria-labelledby="demo-row-radio-buttons-group-label"
                                                name="row-radio-buttons-group"
                                                defaultValue={"Default"}
                                            >
                                                <FormControlLabel value="on" control={<Radio />} label="ON" />
                                                <FormControlLabel value="off" control={<Radio />} label="OFF" />
                                                <FormControlLabel value="Default" control={<Radio />} label="Default" />
                                            </RadioGroup>
                                        </div>
                                        <div>
                                            Enable Turboboost
                                            <RadioGroup
                                                row
                                                aria-labelledby="demo-row-radio-buttons-group-label"
                                                name="row-radio-buttons-group"
                                                defaultValue={"Default"}
                                            >
                                                <FormControlLabel value="on" control={<Radio />} label="ON" />
                                                <FormControlLabel value="off" control={<Radio />} label="OFF" />
                                                <FormControlLabel value="Default" control={<Radio />} label="Default" />
                                            </RadioGroup>
                                        </div>
                                        <div>
                                            Enable Freqency Stepping (Intel P-state Governor)
                                            <RadioGroup
                                                row
                                                aria-labelledby="demo-row-radio-buttons-group-label"
                                                name="row-radio-buttons-group"
                                                defaultValue={"Default"}
                                            >
                                                <FormControlLabel value="on" control={<Radio />} label="ON" />
                                                <FormControlLabel value="off" control={<Radio />} label="OFF" />
                                                <FormControlLabel value="Default" control={<Radio />} label="Default" />
                                            </RadioGroup>
                                        </div>
                                        <div>
                                            Prefetch
                                            <RadioGroup
                                                row
                                                aria-labelledby="demo-row-radio-buttons-group-label"
                                                name="row-radio-buttons-group"
                                                defaultValue={"Default"}
                                            >
                                                <FormControlLabel value="on" control={<Radio />} label="ON" />
                                                <FormControlLabel value="off" control={<Radio />} label="OFF" />
                                                <FormControlLabel value="Default" control={<Radio />} label="Default" />
                                            </RadioGroup>
                                        </div>

                                    </div>
                                </Box>
                            </div>


                        }
                        {activeStep === 3 &&
                            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }} >
                                <Box

                                    sx={{
                                        padding: '20px',
                                        width: '70%',
                                        boxShadow: 3

                                    }}
                                >
                                    <div style={divStyle}>
                                        <div style={titleStyle}>Optional Run System Settings</div>
                                        <div >
                                            CPU choices
                                            <div>

                                                Skylake <Checkbox />
                                                Cascadelake <Checkbox />
                                                Ice Lake <Checkbox />
                                                Default <Checkbox defaultChecked />
                                            </div>
                                        </div>
                                        <div>
                                            Hyperthreading
                                            <div>
                                                ON<Checkbox />
                                                OFF<Checkbox />
                                                Default <Checkbox defaultChecked />
                                            </div>
                                        </div>
                                        <div>
                                            Hugepage
                                            <div>
                                                ON<Checkbox />
                                                OFF<Checkbox />
                                                Default <Checkbox defaultChecked />
                                            </div>
                                        </div>
                                        <div>
                                            Enable Turboboost
                                            <div>
                                                ON<Checkbox />
                                                OFF<Checkbox />
                                                Default <Checkbox defaultChecked />
                                            </div>
                                        </div>


                                        <div>
                                            Enable Freqency Stepping (Intel P-state Governor)
                                            <div>
                                                ON<Checkbox />
                                                OFF<Checkbox />
                                                Default <Checkbox defaultChecked />
                                            </div>
                                        </div>
                                        <div>
                                            Prefetch
                                            <div>
                                                ON<Checkbox />
                                                OFF<Checkbox />
                                                Default <Checkbox defaultChecked />
                                            </div>
                                        </div>
                                        <div>
                                            Compiler Choices
                                            <div>
                                                ICC<Checkbox />
                                                GCC<Checkbox />
                                                LLVM<Checkbox />
                                                Default <Checkbox defaultChecked />
                                            </div>
                                        </div>


                                    </div>
                                </Box>
                            </div>


                        }
                        {activeStep === 5 &&

                            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }} >
                                <Box

                                    sx={{
                                        padding: '20px',
                                        width: '70%',
                                        boxShadow: 3

                                    }}
                                >
                                    <StatusPanel msg={statusMsg} />
                                </Box>
                            </div>
                        }







                        <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
                            <Button
                                color="inherit"
                                disabled={activeStep === 0}
                                onClick={handleBack}
                                sx={{ mr: 1 }}
                            >
                                Back
                            </Button>
                            <Box sx={{ flex: '1 1 auto' }} />
                            {isStepOptional(activeStep) && (
                                <Button color="inherit" onClick={handleSkip} sx={{ mr: 1 }}>
                                    Skip
                                </Button>
                            )}

                            {activeStep === 4 ?

                                <Button onClick={handleSumbitNext}>
                                    Submit

                                </Button> :
                                <Button onClick={handleNext}>
                                    {activeStep === steps.length - 1 ? 'Finish' : 'Next'}

                                </Button>

                            }

                        </Box>
                    </React.Fragment>
                )}
            </Box>
        </div>
    );
}