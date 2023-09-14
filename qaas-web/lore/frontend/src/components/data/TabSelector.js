import React from 'react';

export default function TabSelector({ activeTab, setActiveTab, tabs }) {
    return (
        <div className='tab-container' style={{ backgroundColor: '#f0f0f0' }}>
            {tabs.map(tab => (
                <button
                    key={tab}
                    className={`source-compare-button ${activeTab === tab ? 'active' : ''}`}
                    onClick={() => setActiveTab(tab)}
                >
                    <div className='button-text'>{tab}</div>
                </button>
            ))}
        </div>
    );
}