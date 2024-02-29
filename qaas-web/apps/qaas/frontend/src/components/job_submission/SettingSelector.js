import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { List, ListItem, ListItemText } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import Button from '@mui/material/Button';
import SettingBox from './SettingBox';
import { ThemeProvider } from '@mui/material/styles';
import { JOB_SUB_THEME } from './JobSubUtil';

const SettingsSelector = () => {
    const [settings, setSettings] = useState({});
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

    return (
        <ThemeProvider theme={JOB_SUB_THEME}>

            <div className="settingSelectionContainer">
                <h1>Select from past settings or create a new setting</h1>
                <div >
                    {Object.keys(settings).map((filename) => (
                        <SettingBox text={filename} handleSelectSetting={() => handleSelectSetting(filename)} />

                    ))}
                </div>


                <div>
                    <Button onClick={() => handleSelectSetting()}>Manully create a new setting</Button>

                </div>

            </div>
        </ThemeProvider>
    );

};

export default SettingsSelector;
