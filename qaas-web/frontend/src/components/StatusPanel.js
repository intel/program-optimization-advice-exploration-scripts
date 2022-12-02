import React,{useState} from 'react';
import PropTypes from 'prop-types';
import LinearProgress from '@mui/material/LinearProgress';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

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
export default function StatusPanel({msg}) {
    const [shouldDisplayProgress, setShouldDisplayProgress] = useState(false);
    console.log(msg)
    let msg_num = {
        "QAAS Begin " : 10,
        "Job Begin " : 20,
        "Start Building orig app " : 30,
        "Done Building orig app " : 40,
        "Start Running orig app " : 50,
        "Done Running orig app " : 60,
        "Start Tuning orig app " : 70,
        "Done Tuning orig app " : 80,
        "Start Running tuned app " : 90,
        "Done Running tuned app " : 98,
        "Job End " : 100,
    }
    return (
        <div style={{marginTop:80}}>
            StatusPanel
            {msg != null && <LinearProgressWithLabel value={msg_num[msg]} />}

            {msg != null && <p>{msg}</p>}
        </div>
    )
}