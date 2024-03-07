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

import SettingsSelector from "./SettingSelector";
import SaveSettingButton from "./SaveSettingButton";
export const MachineInfo = ({ input, setInput, selectedMachine, setSelectedMachine, selectedRunMode, setSelectedRunMode }) => {
    const machines = ['fxilab165.an.intel.com', 'intel', 'ancodskx1020.an.intel.com']

    const handleMachineChange = (event) => {
        const machine = event.target.value;
        setSelectedMachine(machine)
    };

    const handleModeChange = (event) => {
        const mode = event.target.value;
        setSelectedRunMode(mode)
    };

    return (
        <div className="centeredBox">
            <div className="infoContent">

                <div className="headerContainer" >
                    <div className="infoTitle">Machine</div>
                    <div className="settingSelector">
                        <SaveSettingButton input={input} />
                        <SettingsSelector setInput={setInput} />
                    </div>


                </div>
                <div>
                    <div className="infoSubTitle">Select Available Machines</div>

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
                <div>
                    <div className="infoSubTitle">Select Run Mode</div>

                    <RadioGroup
                        row
                        aria-labelledby="demo-row-radio-buttons-group-label"
                        name="row-radio-buttons-group"
                        defaultValue={selectedRunMode}
                        onChange={handleModeChange}
                    >
                        <FormControlLabel value="disable_multicompiler_flags" control={<Radio />} label="Disable compiler flags search" />
                        <FormControlLabel value="disable_multicompiler_defaults_and_flags" control={<Radio />} label="Disable multi-compiler and flags search" />
                        <FormControlLabel value="multicompiler" control={<Radio />} label="Multi-compiler" />
                    </RadioGroup>
                </div>

            </div>
        </div>
    );
};
