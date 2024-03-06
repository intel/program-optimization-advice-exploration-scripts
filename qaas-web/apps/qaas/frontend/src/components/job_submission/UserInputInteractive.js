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
import { MachineInfo } from './MachineInfo';
import { JOB_SUB_THEME } from './JobSubUtil';
import StatusPanel from './StatusPanel';
import '../css/input.css'
import { StepperSettingProvider } from '../contexts/StepperSettingContext';
import { useSSE } from '../contexts/SSEContext';

const steps = ['Build Info', 'Run Info', 'Machine Info'];

function StepContent({ stepIndex, input, setInput, formErrors, updateFormErrors, selectedMachine, setSelectedMachine, selectedRunMode, setSelectedRunMode }) {
    switch (stepIndex) {
        case 0:
            return <BuildInfo input={input} setInput={setInput} errors={formErrors} updateFormErrors={updateFormErrors} />;
        case 1:
            return <RunInfo input={input} setInput={setInput} />;
        case 2:
            return <MachineInfo input={input} setInput={setInput} selectedMachine={selectedMachine} setSelectedMachine={setSelectedMachine} selectedRunMode={selectedRunMode} setSelectedRunMode={setSelectedRunMode} />;
        default:
            return null;
    }
}

export default function UserInputStepper() {
    const navigate = useNavigate();
    const [activeStep, setActiveStep] = React.useState(0);
    //initial check of the form
    const [formErrors, setFormErrors] = useState({});
    const { setSSEStatus, startSSEConnection, closeSSEConnection } = useSSE();
    const [selectedMachine, setSelectedMachine] = useState('fxilab165.an.intel.com');
    const [selectedRunMode, setSelectedRunMode] = useState('disable_multicompiler_defaults');

    //user input state, loading the last saved wokring json or empty
    const [input, setInput] = useState(INITIAL_INPUT)
    useEffect(() => {
        const init = async () => {
            const fetchedInput = await fetchInitialInput();
            if (fetchedInput) {
                setInput(fetchedInput); // set the fetched data as the initial state
            }
        };
        init();
    }, []);

    const fetchInitialInput = async () => {
        try {
            const response = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_json_from_file`, {});
            if (response.data) {
                return response.data;
            }
        } catch (error) {
            console.error('Failed to fetch initial input:', error);
            return null;
        }
    };
    // set error
    const updateFormErrors = (field, error) => {
        setFormErrors(prevErrors => ({ ...prevErrors, [field]: error }));
    };

    const hasErrors = () => {
        return Object.values(formErrors).some(error => error !== '');
    };

    const handleNext = () => {
        setActiveStep((prevActiveStep) => prevActiveStep + 1);
    };


    const handleSumbitNext = () => {
        setActiveStep((prevActiveStep) => prevActiveStep + 1);
        startSSEConnection();


        //call backend
        setSSEStatus(true)
        axios.post(`${process.env.REACT_APP_API_BASE_URL}/create_new_run`, { input: input, machine: selectedMachine, mode: selectedRunMode })
            .then((response) => {
                setSSEStatus(false)
                //jump to results directly after create new run
                return () => {
                    closeSSEConnection()

                }
            }
            )

        //navigate to results page immediately
        navigate('/results');


    };


    const handleBack = () => {
        setActiveStep((prevActiveStep) => prevActiveStep - 1);
    };



    //state
    //socket

    /******************************************************************* Finish prepare Written Code *************************************************/

    return (
        <StepperSettingProvider>

            <ThemeProvider theme={JOB_SUB_THEME}>

                <div className='jobSubContainer'>

                    <Stepper activeStep={activeStep}>
                        {steps.map((label, index) => {
                            const stepProps = {};
                            const labelProps = {};


                            return (
                                <Step key={label} {...stepProps}>
                                    <StepLabel {...labelProps}>{label}</StepLabel>
                                </Step>
                            );
                        })}
                    </Stepper>

                    <div className="contentAndNavigation">
                        <div>


                            <StepContent stepIndex={activeStep} input={input} setInput={setInput} formErrors={formErrors}
                                updateFormErrors={updateFormErrors} selectedMachine={selectedMachine} setSelectedMachine={setSelectedMachine}
                                selectedRunMode={selectedRunMode} setSelectedRunMode={setSelectedRunMode}
                            />

                            <div className='navButton'>
                                <Button color="inherit" disabled={activeStep === 0} onClick={handleBack}>Back</Button>


                                {activeStep === steps.length - 1 ?

                                    <Button onClick={handleSumbitNext} disabled={hasErrors()}>
                                        Submit

                                    </Button> :
                                    <Button onClick={handleNext} disabled={hasErrors()}>
                                        {activeStep === steps.length - 1 ? '' : 'Next'}

                                    </Button>

                                }
                            </div>


                        </div>

                    </div>
                </div>
            </ThemeProvider>
        </StepperSettingProvider>

    );
}