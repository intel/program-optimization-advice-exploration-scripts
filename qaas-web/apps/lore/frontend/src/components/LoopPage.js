import React, { useState, useEffect } from 'react';
import TopBar from './TopBar';
import Title from './Title';
import './css/loop.css'
import SourceCodeCompareTab from './data/SourceCodeCompareTab';
import StaticFeatureList from './data/StaticFeatureList';
import HardwareDropdown from './HardwareDropdown';
import SpeedupGraphCompareTab from './graphs/SpeedupGraphCompareTab';
import MutationTable from './data/MutationTable';
import DropdownList from './data/DropdownList';
import SpeedupFormula from './formulas/SpeedupFormula';
import axios from 'axios';
import SpeedupTable from './data/SpeedupTable';
import SpeedupGraphsTab from './graphs/SpeedupGraphsTab';
import { useLocation } from 'react-router-dom';
import DOMPurify from 'dompurify';

function LoopPage() {
    const location = useLocation();

    const query_params = new URLSearchParams(location.search);
    const pageIsloading = query_params.get("loading") === "true";

    //used to detemine specific application
    const workload = query_params.get('workload');
    const program = query_params.get('program');
    const workload_version = query_params.get('workload_version');
    //used to determine specific loop
    const file = query_params.get('file');
    const function_name = query_params.get('function');
    const line = query_params.get('line');
    const source_id = query_params.get('source_id');

    //get all speedup data to use across different components
    const [data, setData] = useState([]);
    const [current_src_loop_id, setCurrentSrcLoopId] = useState(null);

    //to to open mutation page

    // console.log("source_id", source_id)

    useEffect(() => {

        axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_all_speedup_data_for_specific_loop`, {
            file,
            function: function_name,
            line,
            workload,
            program,
            workload_version: workload_version,
        })
            .then(response => {
                setData(response.data['speed_up_data']);
                setCurrentSrcLoopId(response.data['current_src_loop_id'])

            })
            .catch(error => {
                console.error('Error fetching data: ', error);
            });
    }, [file, function_name, line, workload, program, workload_version]);


    if (pageIsloading || !current_src_loop_id) {
        return <div>Loading, please wait...</div>
    }

    return (

        <div >
            <TopBar />
            <div className='content-container'>
                <div className='page-container'>
                    {/* titles overall info about the run */}

                    <div className="component-spacing" >
                        <div>
                            <Title text={`Benchmark: ${workload} ${workload_version}`} />

                            <Title text={`Application: ${program}`} />
                        </div>

                        <div>
                            <h2 id="ttl2" >{`File: ${file}`}</h2>
                            <h2 id="ttl2" >{`Function: ${function_name}`}</h2>
                            <h2 id="ttl2" >{`Line: ${line}`}</h2>

                        </div>
                    </div>

                    {/* baseline source code and static features */}
                    <div className='vertical-spacing'></div>
                    <div className="component-spacing">
                        <div>
                            <h4 id="ttl3" >Baseline source code</h4>
                        </div>

                        <div>
                            <h4 id="ttl3" >Static features of processed baseline</h4>
                        </div>

                    </div>

                    {/* source code component */}
                    {/* static features count component */}
                    <div className="component-spacing-center">
                        <div className='margin-right'>
                            <SourceCodeCompareTab
                                current_src_loop_id={current_src_loop_id}

                            />
                        </div>
                        <div >
                            <StaticFeatureList
                                current_src_loop_id={current_src_loop_id}
                            />
                        </div>
                    </div>

                    {/* title for performace summary and cpu selection */}
                    <div className="component-spacing">

                        <div>
                            <h4 id="ttl3" >Performance summary</h4>
                        </div>

                        <div>
                            <HardwareDropdown

                                current_src_loop_id={current_src_loop_id}

                            />
                        </div>
                    </div>

                    {/* speedup graph */}
                    <div>
                        <SpeedupGraphCompareTab
                            current_src_loop_id={current_src_loop_id}
                            data={data}
                        />
                    </div>
                    <div className='vertical-spacing'></div>

                    <div>
                        <SpeedupFormula level={'loop'} />
                    </div>
                    <div className='vertical-spacing'></div>


                    {/* map list of all compiler choices to dropdown compoent */}
                    <DropdownList
                        data={data}
                        titleKey={(vendor_version, vendor_data) => vendor_version}
                    >
                        {(vendor_version, vendor_data) => (
                            <>
                                <SpeedupGraphsTab data={DOMPurify.sanitize(vendor_data)} />
                                <SpeedupTable data={DOMPurify.sanitize(vendor_data)} current_src_loop_id={current_src_loop_id} source_id={source_id}
                                />
                            </>
                        )}
                    </DropdownList>


                    <div>
                        <h4 id="ttl3" >List of mutations</h4>
                    </div>
                    <MutationTable
                        source_id={source_id}
                        data={data}

                    />

                </div>
            </div>


        </div>


    );


}

export default LoopPage;
