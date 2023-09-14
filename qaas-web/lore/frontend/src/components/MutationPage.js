import React, { useState, useEffect } from 'react';
//model allows user to see a componet on top of everything else
import { Modal } from 'antd';
import MutatedSourceCode from './data/mutations/MutatedSourceCode';
import MutatationExecutionCycles from './data/mutations/MutatationExecutionCycles';
import SpeedupFormula from './formulas/SpeedupFormula';
import DropdownList from './data/DropdownList';
import MutationSpeedupGraph from './graphs/MutationSpeedupGraph';
import DynamicMetricsTables from './data/mutations/DynamicMetricsTables';
export default function MutationPage({ open, data, onOk, onCancel, current_src_loop_id, mutationPerformanceData }) {





    if (!mutationPerformanceData) {
        return <div>Mutation Data Loading, please wait...</div>
    }
    return (

        <Modal title="Row Details" open={open} onOk={onOk} onCancel={onCancel} width={1000}>
            <>
                <div>
                    <h4 id="ttl3" >Mutated source code</h4>
                </div>
                <MutatedSourceCode data={data} current_src_loop_id={current_src_loop_id} />

                <div>
                    <h4 id="ttl3" >Execution cycles</h4>
                </div>
                <MutatationExecutionCycles table_data={mutationPerformanceData} />
                <div>
                    <h4 id="ttl3" >Details by configuration</h4>
                </div>
                <SpeedupFormula level={'mutation'} />

                <DropdownList
                    data={mutationPerformanceData}
                    titleKey={(vendor_version, vendor_data) => vendor_version}
                >
                    {(vendor_version, vendor_data) => (
                        <>

                            {/* everything in drop down */}
                            <MutationSpeedupGraph vendor_data={vendor_data} />

                            <DynamicMetricsTables current_src_loop_id={current_src_loop_id} current_mutation_number={vendor_data.mutation} />

                        </>
                    )}
                </DropdownList>


            </>
        </Modal>
    );
}
