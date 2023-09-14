import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CodeContainer from '../CodeContainer';
export default function MutatedSourceCode({ data, current_src_loop_id }) {

    const [code, setCode] = useState('');


    useEffect(() => {
        axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_lore_mutated_source_code_for_specific_mutation`, {
            current_src_loop_id: current_src_loop_id,
            mutation_number: data['mutation']
        })
            .then(response => {
                setCode(response.data.mutation);
            })
            .catch(error => {
                console.error('Error fetching data: ', error);
            });
    }, [current_src_loop_id, data]);

    return (
        <div>

            <CodeContainer code={code} />

        </div>
    );
}
