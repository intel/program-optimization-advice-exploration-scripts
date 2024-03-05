import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import LinearProgress from '@mui/material/LinearProgress';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import "react-step-progress-bar/styles.css";
import { ProgressBar, Step } from "react-step-progress-bar";
import CircleIcon from '@mui/icons-material/Circle';
let colormap = require('colormap')

export default function StatusPanel({ msg }) {

    let msgs = [
        "Job Begin",
        "Start Building orig app ",
        "Done Building orig app ",
        "Start Running orig app ",
        "Done Running orig app ",
        "Start Tuning orig app ",
        "Done Tuning orig app ",
        "Start Running tuned app ",
        "Done Running tuned app ",
        "Job End",
    ]
    let color_arr = colormap({
        colormap: 'jet',
        nshades: 10,
        format: 'hex',
        alpha: 1
    })
    let index_of_msg = msgs.indexOf(msg)
    return (
        <div className="centeredBox">
            <div className="infoContent">
                <div className="infoSubTitle">StatusPanel</div>


                {index_of_msg > -1 &&
                    <ProgressBar
                        percent={10 * (index_of_msg + 1)}
                        filledBackground="linear-gradient(to right, #e3f2fd, #0d47a1)"
                    >
                        {color_arr.map(c =>
                            <Step >
                                {({ accomplished, position }) => (
                                    <CircleIcon sx={{ color: c }} />
                                )}
                            </Step>
                        )
                        }

                    </ProgressBar>
                }

                {index_of_msg > -1 &&
                    <div>
                        {msgs.map((m, i) =>
                            < div style={{ color: color_arr[i] }} >
                                {m}
                            </div>
                        )
                        }
                    </div>
                }
            </div>

        </div>
    )
}