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


export default function UserInput({ setTimestamps }) {
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

    //data
    // const envCols = [
    //     { field: 'name', headerName: 'name', width: 50, editable: true },
    //     { field: 'value', headerName: 'value', width: 50, editable: true },
    // ];
    const envRows = [
        { id: 1, name: 'name1', value: 'value1' },
        { id: 2, name: 'name2', value: 'value2' },
    ];

    //state
    const [envrows, setEnvRows] = useState(envRows);
    //socket
    const [buttonStatus, setButtonStatus] = useState(false);
    const [statusMsg, setStatusMsg] = useState("");



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
                    APP_RUN_CMD: "",
                    APP_ENV_MAP: {}
                }
            },
            compiler: {
                USER_CC: "",
                USER_CC_VERSION: "",
                USER_C_FLAGS: "",
                USER_CXX_FLAGS: "",
                USER_FC_FLAGS: "",
                USER_LINK_FLAGS: "",
                USER_TARGET: "",
                USER_TARGET_LOCATION: ""
            }
        }
    )


    //use effect
    // let endPoint = "http://127.0.0.1:5000";
    useEffect(() => {
        // let endPoint = "http://10.241.129.38:5000";
        let endPoint = "http://localhost:5002/";
        // let namespace = "/test"
        if (buttonStatus === true) {

            // const socket = io("localhost:5000/", {
            //     transports: ["websocket"],
            //     cors: {
            //       origin: "http://localhost:3000/",
            //     },
            //   });
            const path = endPoint
            // const socket = io.connect(`${endPoint}`, {
            //     // 'autoConnect': false
            // })
            // const socket = io.connect()

            // const socket = io.of(endPoint+namespace)

            // socket.on("connect", (data) => {
            //     console.log(data);
            // });
            // const socket = io(endPoint, {
            //     autoConnect: false
            // });
            // const manager = socket.io;

            // const manager = new Manager(endPoint, {
            //     autoConnect: true
            // });

            // const socket = manager.socket("/");

            // manager.open((err) => {
            //     if (err) {
            //         console.log(err)
            //     } else {
            //         // the connection was successfully established
            //         console.log("successfully connected")
            //     }
            // });
            // socket.on("connect_error", (error) => {
            //     console.log(error)
            // });
            // io = require("socket.io-client")
            // let socket = io.connect("http://localhost:5000");
            // let socket = io.connect(`${endPoint}`);
            // console.log("socket is ", socket)
            // setSocketInstance(socket);
            // socket.emit("data", "test from frontend");
            // socket.on("test", (data) => {
            //     console.log("data from backend", data);
            //     setStatusMsg(data['broadcast_data'])
            // });


            // socket.on("data", (data) => {
            //     console.log(data);
            // });
            // setLoading(false);

            // socket.on("disconnect", (data) => {
            //     console.log(data);
            // });
            // return function cleanup() {
            //     socket.disconnect();
            // };


        }
    }, [buttonStatus]);
    //function

    const handleLaunchRunClick = (e) => {
        // setIsRunning(true)
        // setShouldShowLoading(true)
        setButtonStatus(true)
        axios.post("/create_new_timestamp", input)
            .then((response) => {

                // setTimestamps(preState => [
                //     ...preState,
                //     response.data['timestamp']
                // ])
                setButtonStatus(false)
                // setIsRunning(false)
                // setShouldShowLoading(false)
                // console.log(JSON.parse(response.data['timestamp']))
            })

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
    // const handleEdit = (i) => {
    //     setEdit(!isEdit);
    // };
    // const handleSave = () => {
    //     setEdit(!isEdit);
    //     setEnvRows(envrows);
    //     setDisable(true);
    //     setOpen(true);
    // };
    // const handleInputChange = (e, index) => {
    //     setDisable(false);
    //     const { name, value } = e.target;
    //     const list = [...envrows];
    //     list[index][name] = value;
    //     setEnvRows(list);
    // };
    return (
        <div style={{ marginTop: 80 }}>
            <div style={splitScreen}>
                <div style={leftPane}>
                    <Box
                        sx={{
                            border: '1px dashed grey',
                            padding: '20px'

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

                        <div style={divStyle}>
                            <div style={titleStyle}>System Settings</div>
                            <div style={divStyle}>
                                CPU choices
                                Skylake <Checkbox />
                                Cascadelake <Checkbox defaultChecked />
                                Ice Lake <Checkbox defaultChecked />

                            </div>
                            <div>
                                Turboboost  ON<Checkbox defaultChecked />  OFF<Checkbox />
                            </div>
                            <div>
                                Hyperthreading  ON<Checkbox defaultChecked />  OFF<Checkbox defaultChecked />
                            </div>
                            <div>
                                Hugepage  ON<Checkbox />  OFF<Checkbox defaultChecked />
                            </div>
                            <div>
                                Intel P-state Governor  ON<Checkbox />  OFF<Checkbox defaultChecked />
                            </div>
                            <div>
                                Prefetch  ON<Checkbox />  OFF<Checkbox defaultChecked />
                            </div>

                        </div>
                    </Box>
                </div>
                <div style={rightPane}>

                    <Box
                        sx={{
                            border: '1px dashed grey',
                            padding: '20px',


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
                                <TextField fullWidth sx={{ pr: '5px', pt: '5px' }} label="Data Download Path" id="outlined-basic" variant="outlined"
                                    onChange={
                                        (event) => {
                                            const s = { ...input }
                                            s.application.RUN.APP_RUN_CMD = event.target.value
                                            setInput({ ...s })
                                        }
                                    }
                                />
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
                                                    <TableCell contenteditable='true' align="center">{row.name}</TableCell>
                                                    <TableCell contenteditable='true' align="center">{row.value}</TableCell>
                                                    <TableCell align="center"><DeleteIcon onClick={() => handleDelete(i)} /></TableCell>


                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                                <AddIcon style={{ padding: '10px' }} onClick={() => handleCreate()} />
                            </div>

                        </div>
                        <Box sx={{
                            border: '1px dashed grey',
                            padding: '20px'

                        }}>
                            <StatusPanel msg={statusMsg} />
                        </Box>
                    </Box>

                </div>




            </div>
            <Button variant="contained" type="button" onClick={() => handleLaunchRunClick()}>Launch run button</Button >


        </div>
    )
}