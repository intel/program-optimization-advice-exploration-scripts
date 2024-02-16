import { updateState } from "./JobSubUtil";
import React, { useState, useEffect } from 'react';

import Checkbox from '@mui/material/Checkbox';

export const OptionalRunInfo = ({ input, setInput }) => {

    const handleCheckboxChange = (option, value, isChecked) => {
        const path = ['system', 'SEARCH_OPTIONS', option];

        const currentValues = input.system.SEARCH_OPTIONS[option] || [];

        // add or remove the value based on the isChecked flag
        const updatedValues = isChecked
            ? [...new Set([...currentValues, value])] //prevent duplicates
            : currentValues.filter((item) => item !== value);

        // update the state 
        updateState(setInput, path, updatedValues);
    };


    return (
        <div className="centeredBox">
            <div className="infoContent">
                <div >
                    <div className="infoTitle">Optional Run System Settings</div>
                    <div >
                        <div className="infoSubTitle">CPU choices</div>
                        <div>

                            Skylake
                            <Checkbox
                                checked={input.system.SEARCH_OPTIONS.CPU.includes('Skylake')}
                                onChange={(e) => handleCheckboxChange('CPU', 'Skylake', e.target.checked)}
                            />
                            Cascadelake
                            <Checkbox
                                checked={input.system.SEARCH_OPTIONS.CPU.includes('Cascadelake')}
                                onChange={(e) => handleCheckboxChange('CPU', 'Cascadelake', e.target.checked)}
                            />
                            Ice Lake
                            <Checkbox
                                checked={input.system.SEARCH_OPTIONS.CPU.includes('Ice Lake')}
                                onChange={(e) => handleCheckboxChange('CPU', 'Ice Lake', e.target.checked)}
                            />
                            Default <Checkbox defaultChecked
                                checked={input.system.SEARCH_OPTIONS.CPU.includes('Default')}
                                onChange={(e) => handleCheckboxChange('CPU', 'Default', e.target.checked)}

                            />
                        </div>
                    </div>
                    <div>
                        <div className="infoSubTitle">Hyperthreading</div>


                        <div>
                            ON
                            <Checkbox
                                checked={input.system.SEARCH_OPTIONS.HYPERTHREADING.includes('ON')}
                                onChange={(e) => handleCheckboxChange('HYPERTHREADING', 'ON', e.target.checked)}
                            />
                            OFF
                            <Checkbox
                                checked={input.system.SEARCH_OPTIONS.HYPERTHREADING.includes('OFF')}
                                onChange={(e) => handleCheckboxChange('HYPERTHREADING', 'OFF', e.target.checked)}
                            />
                            Default <Checkbox defaultChecked
                                checked={input.system.SEARCH_OPTIONS.HYPERTHREADING.includes('Default')}
                                onChange={(e) => handleCheckboxChange('HYPERTHREADING', 'Default', e.target.checked)}

                            />
                        </div>
                    </div>
                    <div >
                        <div className="infoSubTitle">Hugepage</div>


                        <div>
                            ON<Checkbox
                                checked={input.system.SEARCH_OPTIONS.HUGEPAGE.includes('ON')}
                                onChange={(e) => handleCheckboxChange('HUGEPAGE', 'ON', e.target.checked)}
                            />
                            OFF<Checkbox
                                checked={input.system.SEARCH_OPTIONS.HUGEPAGE.includes('OFF')}
                                onChange={(e) => handleCheckboxChange('HUGEPAGE', 'OFF', e.target.checked)}
                            />
                            Default <Checkbox defaultChecked
                                checked={input.system.SEARCH_OPTIONS.HUGEPAGE.includes('Default')}
                                onChange={(e) => handleCheckboxChange('HUGEPAGE', 'Default', e.target.checked)}

                            />
                        </div>
                    </div>
                    <div >
                        <div className="infoSubTitle">Enable Turboboost</div>

                        <div>
                            ON<Checkbox
                                checked={input.system.SEARCH_OPTIONS.TURBO_BOOST.includes('ON')}
                                onChange={(e) => handleCheckboxChange('TURBO_BOOST', 'ON', e.target.checked)}
                            />
                            OFF<Checkbox
                                checked={input.system.SEARCH_OPTIONS.TURBO_BOOST.includes('OFF')}
                                onChange={(e) => handleCheckboxChange('TURBO_BOOST', 'OFF', e.target.checked)}
                            />
                            Default <Checkbox defaultChecked
                                checked={input.system.SEARCH_OPTIONS.TURBO_BOOST.includes('Default')}
                                onChange={(e) => handleCheckboxChange('TURBO_BOOST', 'Default', e.target.checked)}
                            />
                        </div>
                    </div>


                    <div >
                        <div className="infoSubTitle">Enable Freqency Stepping (Intel P-state Governor)</div>


                        <div>
                            ON<Checkbox
                                checked={input.system.SEARCH_OPTIONS.FREQ_SCALING.includes('ON')}
                                onChange={(e) => handleCheckboxChange('FREQ_SCALING', 'ON', e.target.checked)}
                            />
                            OFF<Checkbox
                                checked={input.system.SEARCH_OPTIONS.FREQ_SCALING.includes('OFF')}
                                onChange={(e) => handleCheckboxChange('FREQ_SCALING', 'OFF', e.target.checked)}
                            />
                            Default <Checkbox defaultChecked
                                checked={input.system.SEARCH_OPTIONS.FREQ_SCALING.includes('Default')}
                                onChange={(e) => handleCheckboxChange('FREQ_SCALING', 'Default', e.target.checked)}

                            />
                        </div>
                    </div>
                    <div >
                        <div className="infoSubTitle">Prefetch</div>


                        <div>
                            ON<Checkbox
                                checked={input.system.SEARCH_OPTIONS.PREFETCH.includes('ON')}
                                onChange={(e) => handleCheckboxChange('PREFETCH', 'ON', e.target.checked)}
                            />
                            OFF<Checkbox
                                checked={input.system.SEARCH_OPTIONS.PREFETCH.includes('OFF')}
                                onChange={(e) => handleCheckboxChange('PREFETCH', 'OFF', e.target.checked)}
                            />
                            Default <Checkbox defaultChecked
                                checked={input.system.SEARCH_OPTIONS.PREFETCH.includes('Default')}
                                onChange={(e) => handleCheckboxChange('PREFETCH', 'Default', e.target.checked)}

                            />
                        </div>
                    </div>
                    <div>
                        <div className="infoSubTitle">Compiler Choices</div>


                        <div>
                            ICC<Checkbox
                                checked={input.system.SEARCH_OPTIONS.COMPILER.includes('ICC')}
                                onChange={(e) => handleCheckboxChange('COMPILER', 'ICC', e.target.checked)}
                            />
                            GCC<Checkbox
                                checked={input.system.SEARCH_OPTIONS.COMPILER.includes('GCC')}
                                onChange={(e) => handleCheckboxChange('COMPILER', 'GCC', e.target.checked)}
                            />
                            LLVM<Checkbox
                                checked={input.system.SEARCH_OPTIONS.COMPILER.includes('LLVM')}
                                onChange={(e) => handleCheckboxChange('COMPILER', 'LLVM', e.target.checked)}
                            />
                            Default <Checkbox defaultChecked
                                checked={input.system.SEARCH_OPTIONS.COMPILER.includes('Default')}
                                onChange={(e) => handleCheckboxChange('COMPILER', 'Default', e.target.checked)}
                            />
                        </div>
                    </div>


                </div>
            </div>
        </div>
    );
};
