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
        "Start Running orig app ",
        "Start Tuning orig app ",
        "Start Running tuned app ",
        "Job End",
    ]
    let color_arr = colormap({
        colormap: 'jet',
        nshades: msgs.length,
        format: 'hex',
        alpha: 1
    })

    const [countdown, setCountdown] = useState(null);

    useEffect(() => {
        if (msg === "Job End") {
            setCountdown(5);
        }
    }, [msg]);
    useEffect(() => {
        if (countdown === null || countdown <= 0) return;
        const intervalId = setInterval(() => {
            setCountdown(countdown - 1);
        }, 1000);

        return () => clearInterval(intervalId);
    }, [countdown]);
    //reload the page when count down is 0
    useEffect(() => {
        if (countdown === 0) {
            window.location.reload();
        }
    }, [countdown]);
    let index_of_msg = msgs.indexOf(msg)
    let percent = (index_of_msg / (msgs.length - 1)) * 100;

    return (
        <div className="centeredBox">
            <div className="infoContent">
                <div className="infoSubTitle">StatusPanel</div>

                {index_of_msg > -1 &&
                    <ProgressBar
                        percent={percent}
                        filledBackground="linear-gradient(to right, #e3f2fd, #0d47a1)"
                    >
                        {color_arr.map((c, index) => (
                            <Step key={index}>
                                {({ accomplished }) => (
                                    <CircleIcon sx={{ color: c }} />
                                )}
                            </Step>
                        ))}
                    </ProgressBar>
                }

                {index_of_msg > -1 &&
                    <div>
                        {msgs.map((m, i) => (
                            <div key={i} style={{ color: color_arr[i] }}>
                                {m}
                            </div>
                        ))}
                    </div>
                }
                {countdown !== null && (
                    <Typography variant="body1" style={{ marginTop: '10px' }}>
                        Refreshing in {countdown} seconds...
                    </Typography>
                )}
            </div>
        </div>
    );
}