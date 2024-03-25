//this context is used to share settings for differetn steps in stepper
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { REACT_APP_API_BASE_URL } from '../Constants';
// initial context state
const initialContextState = {
    selectedSetting: '',
    settings: [],
    updateSetting: () => { },
    fetchSettings: () => { },
};

const StepperSettingContext = createContext(initialContextState);

export const StepperSettingProvider = ({ children }) => {
    const [selectedSetting, setSelectedSetting] = useState(initialContextState.selectedSetting);
    const [settings, setSettings] = useState(initialContextState.settings);

    const fetchSettings = async (forceUpdate = false) => {
        if (settings.length > 0 && !forceUpdate) return; // no fetch if settings are already loaded unless forced

        try {
            const response = await axios.get(`${REACT_APP_API_BASE_URL}/get_all_input_settings`);
            if (response.data && response.data.filenames) {
                setSettings(response.data.filenames);
            }
        } catch (error) {
            console.error('Error fetching settings:', error);
        }
    };

    const updateSetting = (newSetting) => {
        setSelectedSetting(newSetting);
    };

    useEffect(() => {
        fetchSettings();
    }, []);

    return (
        <StepperSettingContext.Provider value={{ selectedSetting, settings, updateSetting, fetchSettings }}>
            {children}
        </StepperSettingContext.Provider>
    );
};

// hook to use the stepper setting context
export const useStepper = () => useContext(StepperSettingContext);
