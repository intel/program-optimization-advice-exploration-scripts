import React, { useState, useEffect } from 'react';
import { ThemeProvider } from '@mui/material/styles';
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
import { JOB_SUB_THEME } from './JobSubUtil';
import StatusPanel from './StatusPanel';
import '../css/input.css'
import { useLocation } from 'react-router-dom';

const steps = ['Build Info', 'Run Info', 'Golden Run System Settings', 'Optional Run System Settings', 'Validation and Domain Specific Rate', 'Status Info'];

export default function UserInputStepper() {
    const location = useLocation();
    const selectedSettingData = location.state?.data;
    const navigate = useNavigate();
    const [activeStep, setActiveStep] = React.useState(0);
    const [skipped, setSkipped] = React.useState(new Set());
    const [statusMsg, setStatusMsg] = useState("");
    const [SSEStatus, setSSEStatus] = useState(false);
    //user input state
    const [input, setInput] = useState(selectedSettingData || INITIAL_INPUT)

    //initial check of the form
    const getInitialFormErrors = () => {
        if (input.application && input.application.APP_NAME && input.application.APP_NAME.trim() !== '') {
            return {};
        }
        return { APP_NAME: 'App Name is required' };
    };
    const [formErrors, setFormErrors] = useState(getInitialFormErrors);


    // set error
    const updateFormErrors = (field, error) => {
        setFormErrors(prevErrors => ({ ...prevErrors, [field]: error }));
    };

    const hasErrors = () => {
        return Object.values(formErrors).some(error => error !== '');
    };
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
            console.log("got mes", e.data)
            setStatusMsg(e.data)
        }
        sse.onopen = e => {
            console.log("connection open", e.data)

        }
        sse.onmessage = e => {
            console.log("got mes", e.data)

            handleStream(e)
        }
        sse.addEventListener('ping', e => {
            console.log("event listener got mes", e.data)

            setStatusMsg(e.data)
        })
        sse.onerror = e => {
            //GOTCHA - can close stream and 'stall'
            console.log("close stream", e.data)

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

    //see results button click
    const handleFinishButtonClick = () => {
        navigate('/results');
    };
    //state
    //socket

    /******************************************************************* Finish prepare Written Code *************************************************/

    return (
        <ThemeProvider theme={JOB_SUB_THEME}>

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

                            {activeStep === 0 && <BuildInfo input={input} setInput={setInput} errors={formErrors} updateFormErrors={updateFormErrors} />}
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

                                    <Button onClick={handleSumbitNext} disabled={hasErrors()}>
                                        Submit and Save Input Settings

                                    </Button> :
                                    <Button onClick={handleNext} disabled={hasErrors()}>
                                        {activeStep === steps.length - 1 ? 'Finish' : 'Next'}

                                    </Button>

                                }
                            </div>


                        </div>
                    )}
                </div>
            </div>
        </ThemeProvider>

    );
}