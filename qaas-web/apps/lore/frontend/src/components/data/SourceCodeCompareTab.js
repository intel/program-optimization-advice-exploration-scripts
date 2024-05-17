import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../css/loop.css'
import TabSelector from './TabSelector';
import CodeContainer from './CodeContainer';
import { REACT_APP_API_BASE_URL } from '../Constants';
function SourceCodeCompareTab({ current_src_loop_id }) {

    const [activeTab, setActiveTab] = useState('Processed baseline');
    const [code, setCode] = useState({ 'Processed baseline': '' });


    useEffect(() => {
        axios.post(`${REACT_APP_API_BASE_URL}/get_lore_baseline_source_code_for_specific_loop`, {
            current_src_loop_id: current_src_loop_id
        })
            .then(response => {
                setCode(response.data);
            })
            .catch(error => {
                console.error('Error fetching data: ', error);
            });
    }, [current_src_loop_id]);

    const tabs = ['Processed baseline'];
    return (
        <div className='component-background'>
            <TabSelector activeTab={activeTab} setActiveTab={setActiveTab} tabs={tabs} />
            <div className='sub-tab-container'>

                <div className="code-container">
                    <CodeContainer code={code['Processed baseline']} />
                </div>
            </div>
        </div>
    );
}

export default SourceCodeCompareTab;
