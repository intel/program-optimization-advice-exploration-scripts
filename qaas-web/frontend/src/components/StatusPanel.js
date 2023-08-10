import React, { useState } from 'react';
import PropTypes from 'prop-types';
import LinearProgress from '@mui/material/LinearProgress';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import "react-step-progress-bar/styles.css";
import { ProgressBar, Step } from "react-step-progress-bar";
import CircleIcon from '@mui/icons-material/Circle';
let colormap = require('colormap')
function LinearProgressWithLabel(props) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <Box sx={{ width: '100%', mr: 1 }}>
        <LinearProgress variant="determinate" {...props} />
      </Box>
      <Box sx={{ minWidth: 35 }}>
        <Typography variant="body2" color="text.secondary">{`${Math.round(
          props.value,
        )}%`}</Typography>
      </Box>
    </Box>
  );
}
export default function StatusPanel({ msg }) {
  const [shouldDisplayProgress, setShouldDisplayProgress] = useState(false);
  let msgs = [
    "Job Begin ",
    "Start Building orig app ",
    "Done Building orig app ",
    "Start Running orig app ",
    "Done Running orig app ",
    "Start Tuning orig app ",
    "Done Tuning orig app ",
    "Start Running tuned app ",
    "Done Running tuned app ",
    "Job End ",
  ]
  // let color_arr = ['#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#2196f3', '#1e88e5', '#1976d2', '#1565c0', '#0d47a1']
  let color_arr = colormap({
    colormap: 'jet',
    nshades: 10,
    format: 'hex',
    alpha: 1
  })
  let index_of_msg = msgs.indexOf(msg)
  return (
    <div style={{ marginTop: 80 }}>
      StatusPanel
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
        <ul>
          {msgs.map((m, i) =>
            <li style={{ color: color_arr[i] }}>
              {m}
            </li>
          )
          }
        </ul>
      }
      {/* {JSON.stringify(msg_num).indexOf(msg) > -1 && <p>{msg}</p>} */}


    </div>
  )
}