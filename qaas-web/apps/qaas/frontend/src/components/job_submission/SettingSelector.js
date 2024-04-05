import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import { JOB_SUB_THEME } from './JobSubUtil';
import { useStepper } from '../contexts/StepperSettingContext';
import { REACT_APP_API_BASE_URL } from '../Constants';
const SettingsSelector = ({ input, setInput }) => {
    const { selectedSetting, settings, updateSetting, fetchSettings } = useStepper();




    //get all jsons
    useEffect(() => {
        fetchSettings();
    }, []);

    const handleSettingSelect = async (filename) => {
        try {
            const response = await axios.post(`${REACT_APP_API_BASE_URL}/get_json_from_file`, { filename });
            setInput(response.data);
        } catch (error) {
            console.error('Error fetching setting:', error);
        }
    };

    //called after user select item from pulldown
    const handleChange = (event) => {
        const filename = event.target.value;
        updateSetting(filename);
        handleSettingSelect(filename);
    };
    return (
        <ThemeProvider theme={JOB_SUB_THEME}>

            <div className="settingSelectionContainer">

                <FormControl sx={{ minWidth: 200 }}>
                    <InputLabel id="setting-selector-label">Select Past Job Requests</InputLabel>
                    <Select
                        labelId="setting-selector-label"
                        id="setting-selector"
                        value={selectedSetting}
                        label="Select Past Job Requests"
                        onChange={handleChange}
                    >
                        {settings.map((filename) => (
                            <MenuItem key={filename} value={filename}>
                                {filename}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>





            </div>
        </ThemeProvider>
    );

};

export default SettingsSelector;
