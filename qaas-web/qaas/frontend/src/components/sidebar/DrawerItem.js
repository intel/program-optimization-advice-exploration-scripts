// DrawerItem.js
import React from 'react';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const DrawerItem = ({ level, text, path, status, drillDown, parent, children, navigateToSection, selectedItem, hasChildren }) => {
    const isSelected = selectedItem === path;
    let statusColor;
    switch (status) {
        case 'empty': statusColor = 'yellow'; break;
        case 'ongoing': statusColor = 'orange'; break;
        case 'finished': statusColor = 'green'; break;
        default: statusColor = ''; break;
    }
    return (
        <ListItem className='draweritem-list-button'>
            <ListItemButton
                className={`level level${level} ${isSelected ? 'highlight-color' : ''} hover-color`}
                style={{ paddingLeft: `${level * 15}px`, backgroundColor: statusColor }}
                onClick={() => navigateToSection(path, text, parent, children, drillDown)}
            >
                <ListItemText primary={text} />
                {hasChildren && (drillDown ? <ExpandMoreIcon fontSize="medium" /> : <ArrowForwardIosIcon fontSize="small" />)}
            </ListItemButton>
        </ListItem>
    );
};


export default DrawerItem;
