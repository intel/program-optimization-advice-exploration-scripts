import React from 'react';

const LinkBox = ({ href, children }) => {
    return (
        <div className="link-box">
            <a href={href}>{children}</a>
        </div>
    );
};

export default LinkBox;
