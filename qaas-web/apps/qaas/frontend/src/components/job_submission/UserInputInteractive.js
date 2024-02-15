import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Checkbox from '@mui/material/Checkbox';
import StatusPanel from '../StatusPanel';
import Button from '@mui/material/Button';
import axios from "axios";
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Typography from '@mui/material/Typography';
import { useNavigate } from 'react-router-dom'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { INITIAL_INPUT } from './InitialInput';
import { BuildInfo } from './BuildInfo';
import { RunInfo } from './RunInfo';
import { GoldenRunInfo } from './GoldenRunInfo';
import { OptionalRunInfo } from './OptionalRunInfo';
import { ValidationInfo } from './ValidationInfo';
import '../css/input.css'
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

        const sse = new EventSource(`${process.env.REACT_APP_API_BASE_URL}/stream`)

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
        axios.post(`${process.env.REACT_APP_API_BASE_URL}/create_new_run`, input)
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
    const [input, setInput] = useState(INITIAL_INPUT)

    const handleFinishButtonClick = () => {
        setIsLoading(false)
        setShouldLoadHTML(true)
    };
    const isValueInInput = (input_location, value) => {
        return input_location.indexOf[value] > -1
    }

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
        <div className='jobSubContainer'>
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
            <div className="contentAndNavigation">

                {activeStep === steps.length ? (
                    <div>
                        <Typography >
                            All steps completed - you&apos;re finished
                        </Typography>
                        <Button variant="contained" onClick={handleFinishButtonClick} endIcon={<ArrowForwardIcon />}>See Result</Button>
                        <Button onClick={handleReset}>Reset</Button>
                    </div>
                ) : (
                    <div>

                        {activeStep === 0 && <BuildInfo input={input} setInput={setInput} />}
                        {activeStep === 1 && <RunInfo input={input} setInput={setInput} />}
                        {activeStep === 4 && <ValidationInfo input={input} setInput={setInput} />}
                        {activeStep === 2 && <GoldenRunInfo input={input} setInput={setInput} />}
                        {activeStep === 3 && <OptionalRunInfo input={input} setInput={setInput} />}
                        {activeStep === 5 && <StatusPanel msg={statusMsg} />}
                        <div className='navButton'>
                            <Button
                                color="inherit"
                                disabled={activeStep === 0}
                                onClick={handleBack}
                            >
                                Back
                            </Button>
                            {isStepOptional(activeStep) && (
                                <Button color="inherit" onClick={handleSkip} >
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
                        </div>


                    </div>
                )}
            </div>
        </div>
    );
}