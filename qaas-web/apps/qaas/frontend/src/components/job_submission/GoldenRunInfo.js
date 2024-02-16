import { updateState } from "./JobSubUtil";
import React, { useState, useEffect } from 'react';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';

export const GoldenRunInfo = ({ input, setInput }) => {
    const handleChange = (path, event) => {
        const { value } = event.target;
        updateState(setInput, path, value);
    };
    return (
        <div className="centeredBox">
            <div className="infoContent">
                <div >
                    <div className="infoTitle">Golden Run System Settings</div>
                    <div >
                        <div className="infoSubTitle">CPU choices </div>
                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={input.system.USER_OPTION.CPU || "Default"}
                            onChange={(e) => handleChange(['system', 'USER_OPTION', 'CPU'], e)}

                        >
                            <FormControlLabel value="Sky Lake" control={<Radio />} label="Sky Lake" />
                            <FormControlLabel value="Cascade Lake" control={<Radio />} label="Cascade Lake" />
                            <FormControlLabel value="Ice Lake" control={<Radio />} label="Ice Lake" />
                            <FormControlLabel value="Default" control={<Radio />} label="Default" />
                        </RadioGroup>
                    </div>
                    <div>
                        <div className="infoSubTitle">Hyperthreading </div>


                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={input.system.USER_OPTION.HYPERTHREADING || "Default"}
                            onChange={(e) => handleChange(['system', 'USER_OPTION', 'HYPERTHREADING'], e)}
                        >
                            <FormControlLabel value="on" control={<Radio />} label="ON" />
                            <FormControlLabel value="off" control={<Radio />} label="OFF" />
                            <FormControlLabel value="Default" control={<Radio />} label="Default" />
                        </RadioGroup>
                    </div>
                    <div >
                        <div className="infoSubTitle"> Huge Page </div>


                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={input.system.USER_OPTION.HUGEPAGE || "Default"}
                            onChange={(e) => handleChange(['system', 'USER_OPTION', 'HUGEPAGE'], e)}
                        >
                            <FormControlLabel value="on" control={<Radio />} label="ON" />
                            <FormControlLabel value="off" control={<Radio />} label="OFF" />
                            <FormControlLabel value="Default" control={<Radio />} label="Default" />
                        </RadioGroup>
                    </div>
                    <div >
                        <div className="infoSubTitle">Enable Turboboost</div>


                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={input.system.USER_OPTION.TURBO_BOOST || "Default"}
                            onChange={(e) => handleChange(['system', 'USER_OPTION', 'TURBO_BOOST'], e)}
                        >
                            <FormControlLabel value="on" control={<Radio />} label="ON" />
                            <FormControlLabel value="off" control={<Radio />} label="OFF" />
                            <FormControlLabel value="Default" control={<Radio />} label="Default" />
                        </RadioGroup>
                    </div>
                    <div >
                        <div className="infoSubTitle">Enable Freqency Stepping (Intel P-state Governor)</div>


                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={input.system.USER_OPTION.FREQ_SCALING || "Default"}
                            onChange={(e) => handleChange(['system', 'USER_OPTION', 'FREQ_SCALING'], e)}
                        >
                            <FormControlLabel value="on" control={<Radio />} label="ON" />
                            <FormControlLabel value="off" control={<Radio />} label="OFF" />
                            <FormControlLabel value="Default" control={<Radio />} label="Default" />
                        </RadioGroup>
                    </div>
                    <div >
                        <div className="infoSubTitle">Prefetch</div>


                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={input.system.USER_OPTION.PREFETCH || "Default"}
                            onChange={(e) => handleChange(['system', 'USER_OPTION', 'PREFETCH'], e)}
                        >
                            <FormControlLabel value="on" control={<Radio />} label="ON" />
                            <FormControlLabel value="off" control={<Radio />} label="OFF" />
                            <FormControlLabel value="Default" control={<Radio />} label="Default" />
                        </RadioGroup>
                    </div>

                </div>
            </div>
        </div>
    );
};
