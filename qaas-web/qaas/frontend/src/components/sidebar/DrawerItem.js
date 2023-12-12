// DrawerItem.js
import React from 'react';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import InfoIcon from '@mui/icons-material/Info';
import CallMadeIcon from '@mui/icons-material/CallMade';
const DrawerItem = ({ level, text, path, status, drillDown, parent, children, navigateToSection, selectedItem, hasChildren, expandedSections }) => {
    const isSelected = selectedItem === path;
    let statusColor;
    switch (status) {
        case 'empty': statusColor = 'yellow'; break;
        case 'ongoing': statusColor = 'orange'; break;
        case 'finished': statusColor = 'green'; break;
        case 'unclickable': statusColor = 'grey'; break;

        default: statusColor = ''; break;
    }
    //render icon check it if is expanded
    const renderIcon = () => {
        if (drillDown) {
            return <CallMadeIcon fontSize='small' />;
        }

        const isExpanded = expandedSections.includes(path);
        return isExpanded ? < KeyboardArrowDownIcon /> : < KeyboardArrowRightIcon />;
    };
    const handleClick = () => {
        if (status !== 'unclickable') {
            navigateToSection(path, text, parent, children, drillDown);
        }
    };
    return (
        <ListItem className='draweritem-list-button'>
            <ListItemButton
                className={`level level${level} ${isSelected ? 'highlight-color' : ''} hover-color`}
                style={{ paddingLeft: `${level * 15}px`, backgroundColor: statusColor }}
                onClick={handleClick}
            >
                <ListItemText primary={text} />
                {hasChildren && renderIcon()}
            </ListItemButton>
        </ListItem>
    );
};


export default DrawerItem;
