import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import FormControlLabel from '@mui/material/FormControlLabel';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import Paper from '@mui/material/Paper';
import DeleteIcon from '@mui/icons-material/RemoveCircleOutline';
import AddIcon from '@mui/icons-material/AddCircleOutline';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import axios from 'axios';
import Checkbox from '@mui/material/Checkbox';
import { OPTIONAL_BLOCK_THEME } from "./JobSubUtil";
import { ThemeProvider } from '@mui/material/styles';

import SettingsSelector from "./SettingSelector";
import SaveSettingButton from "./SaveSettingButton";
import { REACT_APP_API_BASE_URL } from '../Constants';
export const MachineInfo = ({ input, setInput, selectedMachine, setSelectedMachine, selectedRunMode, setSelectedRunMode }) => {
    const [machines, setMachines] = useState([]);

    useEffect(() => {
        fetchMachines();
    }, []);

    const fetchMachines = async () => {
        try {
            const response = await axios.get(`${REACT_APP_API_BASE_URL}/get_machine_list`);
            setMachines(response.data['machines']);
            //only set if machine has at least one item
            if (response.data['machines'].length > 0) {
                setSelectedMachine(response.data['machines'][0]);
            }
        } catch (error) {
            console.error('Error fetching setting:', error);
        }
    };

    const handleMachineChange = (event) => {
        const machine = event.target.value;
        setSelectedMachine(machine)
    };

    const handleModeChange = (option, isChecked) => {
        setSelectedRunMode(currentModes => {
            let newModes = [...currentModes]; // cp the current state

            if (isChecked) {
                // if 'enable_compiler_flag_exploration' is being checked, make sure 'enable_compiler_exploration' is already checked

                if (option === 'enable_compiler_flag_exploration' && !newModes.includes('enable_compiler_exploration')) {
                    // if it's not, add 'enable_compiler_exploration' first
                    newModes.push('enable_compiler_exploration');
                }
                if (!newModes.includes(option)) {
                    newModes.push(option);
                }
            } else {
                // if the checkbox is unchecked, remove the option
                newModes = newModes.filter(mode => mode !== option);
                // If 'enable_compiler_exploration' is being unchecked, also uncheck 'enable_compiler_flag_exploration'

                // special handling
                if (option === 'enable_compiler_exploration') {
                    newModes = newModes.filter(mode => mode !== 'enable_compiler_flag_exploration');
                }
            }
            return newModes;

        });
    };


    return (
        <div className="centeredBox">
            <div className="infoContent">

                <div className="headerContainer" >
                    <div className="infoTitle">Machine Info</div>
                    <div className="settingSelector">
                        <SaveSettingButton input={input} />
                        <SettingsSelector setInput={setInput} />
                    </div>


                </div>
                <div className="block">
                    <div>
                        <div className="infoSubTitle">Machines For Job Submission</div>

                        <FormControl sx={{ minWidth: 200 }}>
                            <InputLabel id="machine-selector-label">Select Available Machines</InputLabel>
                            <Select
                                labelId="machine-selector-label"
                                id="machine-selector"
                                value={selectedMachine}
                                label="Select Available Machines"
                                onChange={handleMachineChange}
                            >
                                {machines.map((machine) => (
                                    <MenuItem key={machine} value={machine}>
                                        {machine}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </div>
                </div>
                <ThemeProvider theme={OPTIONAL_BLOCK_THEME}>

                    <div className="block optional-block">
                        <div className="blockTitle">Optional</div>


                        <div>
                            <div className="infoSubTitle">Select Run Mode</div>

                            <div>
                                Enable compiler exploration
                                <Checkbox
                                    checked={selectedRunMode.includes('enable_compiler_exploration')}
                                    onChange={(e) => handleModeChange('enable_compiler_exploration', e.target.checked)}
                                />
                                Enable compiler flag exploration
                                <Checkbox
                                    checked={selectedRunMode.includes('enable_compiler_flag_exploration')}
                                    onChange={(e) => handleModeChange('enable_compiler_flag_exploration', e.target.checked)}
                                />

                            </div>

                            {/* <RadioGroup
                        row
                        aria-labelledby="demo-row-radio-buttons-group-label"
                        name="row-radio-buttons-group"
                        defaultValue={selectedRunMode}
                        onChange={handleModeChange}
                    >
                        <FormControlLabel value="disable_multicompiler_defaults_and_flags" control={<Radio />} label="enable compiler exploration" />
                        <FormControlLabel value="disable_multicompiler_flags" control={<Radio />} label="enable compiler flag exploration" />
                    </RadioGroup> */}
                        </div>
                    </div>
                </ThemeProvider>
            </div>
        </div>
    );
};
