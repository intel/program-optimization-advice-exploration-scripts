import { updateState } from "./JobSubUtil";
import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';

import Checkbox from '@mui/material/Checkbox';

export const OptionalRunInfo = ({ input, setInput }) => {

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
                    <div style={titleStyle}>Optional Run System Settings</div>
                    <div >
                        CPU choices
                        <div>

                            Skylake <Checkbox />
                            Cascadelake <Checkbox />
                            Ice Lake <Checkbox />
                            Default <Checkbox defaultChecked />
                        </div>
                    </div>
                    <div>
                        Hyperthreading
                        <div>
                            ON<Checkbox />
                            OFF<Checkbox />
                            Default <Checkbox defaultChecked />
                        </div>
                    </div>
                    <div>
                        Hugepage
                        <div>
                            ON<Checkbox />
                            OFF<Checkbox />
                            Default <Checkbox defaultChecked />
                        </div>
                    </div>
                    <div>
                        Enable Turboboost
                        <div>
                            ON<Checkbox />
                            OFF<Checkbox />
                            Default <Checkbox defaultChecked />
                        </div>
                    </div>


                    <div>
                        Enable Freqency Stepping (Intel P-state Governor)
                        <div>
                            ON<Checkbox />
                            OFF<Checkbox />
                            Default <Checkbox defaultChecked />
                        </div>
                    </div>
                    <div>
                        Prefetch
                        <div>
                            ON<Checkbox />
                            OFF<Checkbox />
                            Default <Checkbox defaultChecked />
                        </div>
                    </div>
                    <div>
                        Compiler Choices
                        <div>
                            ICC<Checkbox />
                            GCC<Checkbox />
                            LLVM<Checkbox />
                            Default <Checkbox defaultChecked />
                        </div>
                    </div>


                </div>
            </div>
        </div>
    );
};
