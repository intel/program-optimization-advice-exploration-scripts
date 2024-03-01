import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { List, ListItem, ListItemText } from '@mui/material';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';

import { useNavigate } from 'react-router-dom';
import Button from '@mui/material/Button';
import SettingBox from './SettingBox';
import { ThemeProvider } from '@mui/material/styles';
import { JOB_SUB_THEME } from './JobSubUtil';

const SettingsSelector = () => {
    const [settings, setSettings] = useState({});
    const [selectedSetting, setSelectedSetting] = useState('');

    const navigate = useNavigate();

    //get all jsons
    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const response = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_all_input_settings`);
                setSettings(response.data);
            } catch (error) {
                console.error('Error fetching settings:', error);
            }
        };

        fetchSettings();
    }, []);

    //select data if select a file pass that file to input other wise use a default empty template
    const handleSelectSetting = (filename) => {
        if (filename) {
            const selectedSettingData = settings[filename];
            navigate('/input', { state: { data: selectedSettingData } });
        } else {
            navigate('/input');
        }
    };

    //called after user select item from pulldown
    const handleChange = (event) => {
        setSelectedSetting(event.target.value);
        handleSelectSetting(event.target.value);
    };

    return (
        <ThemeProvider theme={JOB_SUB_THEME}>

            <div className="settingSelectionContainer">
                <FormControl sx={{ minWidth: 200 }}>
                    <InputLabel id="setting-selector-label">Select Past Settings</InputLabel>
                    <Select
                        labelId="setting-selector-label"
                        id="setting-selector"
                        value={selectedSetting}
                        label="Settings"
                        onChange={handleChange}
                    >
                        {Object.keys(settings).map((filename) => (
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
