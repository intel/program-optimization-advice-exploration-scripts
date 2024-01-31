import React from 'react';

import { Link } from 'react-router-dom';
import ov1Image from '../../imgs/ov1.png';
import ov2Image from '../../imgs/ov2.png';
export default function AMGHACCClickTarget() {
    return (
        <div className="textPageContainer">
            <h1>AMG/HACC click target</h1>
            <p>
            {' '}
                <Link className='link'
                    to="https://datafront-intel.liparad.uvsq.fr/oneview_page/"
                >OneView</Link> {' '}
                does many detailed analyses of source and binary code that are summarized for AMG and HACC
                in Fig. OV1 and Fig. OV2, respectively. The array access efficiency line shows the % of high performance array access instructions executed.
                AMG shows 70% array access efficiency, i.e. 30% non-stride-1 memory accesses. As an algebraic multigrid solver, it accesses varying parts of arrays
                from iteration to iteration, which forces the compiler to generate a lot of non-vector code. In fact,
                OneView estimates nearly a 3X speedup if it were fully vectorized. In contrast, note that OneView portrays HACC (with large dense arrays),
                entirely in green - with no chance for gain. This, together with its very high efficiency
                (see 
                    {' '}
                    <Link className='link'
                        to="/qaas/overview/compiler_comparison#figbestcomp"
                    > Fig. bestcomp</Link>) indicates that HACC will scale well using many more cores.



                {' '}
                <Link className='link'
                    to="/qaas/overview/compiler_comparison"
                >Click back</Link>{' '}
                to compiler comparison.



            </p>

            <div className='multiple-graph-container'>
                <div className='imageContainer'>
                    <img src={ov1Image} alt="ov1Image" />
                </div>
                <div className='imageContainer'>
                    <img src={ov2Image} alt="ov2Image" />
                </div>
            </div>




        </div>
    );


}