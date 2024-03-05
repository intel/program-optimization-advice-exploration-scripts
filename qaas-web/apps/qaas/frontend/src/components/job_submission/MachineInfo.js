import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import FormControlLabel from '@mui/material/FormControlLabel';
import Paper from '@mui/material/Paper';
import DeleteIcon from '@mui/icons-material/RemoveCircleOutline';
import AddIcon from '@mui/icons-material/AddCircleOutline';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';

import SettingsSelector from "./SettingSelector";
import SaveSettingButton from "./SaveSettingButton";
export const MachineInfo = ({ input, setInput, selectedMachine, setSelectedMachine }) => {
    const machines = ['fxilab165.an.intel.com', 'intel', 'ancodskx1020.an.intel.com']

    const handleChange = (event) => {
        const machine = event.target.value;
        setSelectedMachine(machine)
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
                <FormControl sx={{ minWidth: 200 }}>
                    <InputLabel id="machine-selector-label">Select Available Machines</InputLabel>
                    <Select
                        labelId="machine-selector-label"
                        id="machine-selector"
                        value={selectedMachine}
                        label="Select Available Machines"
                        onChange={handleChange}
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
    );
};
