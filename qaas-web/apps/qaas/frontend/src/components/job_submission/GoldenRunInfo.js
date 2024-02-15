import { updateState } from "./JobSubUtil";
import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';

export const GoldenRunInfo = ({ input, setInput }) => {

    const titleStyle = {
        fontSize: '1.5em',
        fontWeight: 'bold'
    };

    const divStyle = {
        padding: '5px'
    };


    return (
        <div className="centeredBox">
            <div className="infoContent">
                <div style={divStyle}>
                    <div style={titleStyle}>Golden Run System Settings</div>
                    <div>
                        CPU choices
                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={"Default"}
                        >
                            <FormControlLabel value="Sky Lake" control={<Radio />} label="Sky Lake" />
                            <FormControlLabel value="Cascade Lake" control={<Radio />} label="Cascade Lake" />
                            <FormControlLabel value="Ice Lake" control={<Radio />} label="Ice Lake" />
                            <FormControlLabel value="Default" control={<Radio />} label="Default" />
                        </RadioGroup>
                    </div>
                    <div>
                        Hyperthreading
                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={"Default"}
                        >
                            <FormControlLabel value="on" control={<Radio />} label="ON" />
                            <FormControlLabel value="off" control={<Radio />} label="OFF" />
                            <FormControlLabel value="Default" control={<Radio />} label="Default" />
                        </RadioGroup>
                    </div>
                    <div>
                        Huge Page
                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={"Default"}
                        >
                            <FormControlLabel value="on" control={<Radio />} label="ON" />
                            <FormControlLabel value="off" control={<Radio />} label="OFF" />
                            <FormControlLabel value="Default" control={<Radio />} label="Default" />
                        </RadioGroup>
                    </div>
                    <div>
                        Enable Turboboost
                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={"Default"}
                        >
                            <FormControlLabel value="on" control={<Radio />} label="ON" />
                            <FormControlLabel value="off" control={<Radio />} label="OFF" />
                            <FormControlLabel value="Default" control={<Radio />} label="Default" />
                        </RadioGroup>
                    </div>
                    <div>
                        Enable Freqency Stepping (Intel P-state Governor)
                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={"Default"}
                        >
                            <FormControlLabel value="on" control={<Radio />} label="ON" />
                            <FormControlLabel value="off" control={<Radio />} label="OFF" />
                            <FormControlLabel value="Default" control={<Radio />} label="Default" />
                        </RadioGroup>
                    </div>
                    <div>
                        Prefetch
                        <RadioGroup
                            row
                            aria-labelledby="demo-row-radio-buttons-group-label"
                            name="row-radio-buttons-group"
                            defaultValue={"Default"}
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
