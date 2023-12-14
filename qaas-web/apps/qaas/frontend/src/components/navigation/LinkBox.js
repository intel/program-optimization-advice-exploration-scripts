import React from 'react';
import { useNavigate } from 'react-router-dom';

const LinkBox = ({ path, text }) => {
    const navigate = useNavigate();
    const handleNavigate = () => {
        navigate(path);

    };
    return (
        <div className="link-box" onClick={handleNavigate}>
            {text}
        </div>
    );
};

export default LinkBox;
