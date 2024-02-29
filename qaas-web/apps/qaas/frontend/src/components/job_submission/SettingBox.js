import React from 'react';

const SettingBox = ({ handleSelectSetting, text }) => {

    return (
        <div className="link-box" onClick={handleSelectSetting}>
            {text}
        </div>
    );
};

export default SettingBox;
