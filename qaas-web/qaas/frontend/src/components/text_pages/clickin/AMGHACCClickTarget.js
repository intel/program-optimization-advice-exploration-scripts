import React from 'react';

import { Link } from 'react-router-dom';
import ov1Image from '../../imgs/ov1.png';
import ov2Image from '../../imgs/ov2.png';
export default function AMGHACCClickTarget() {
    return (
        <div className="textPageContainer">
            <h1>AMG/HACC click target</h1>
            <p>

                OneView does many detailed analyses of source and binary code that are summarized here for AMG and HACC
                in Fig. OV1. Array access efficiency shows the % of high performance array access instructions,
                so AMG has 30% non-stride 1 memory accesses; as a multigrid solver, it accesses just parts of arrays
                on some iterations. This, in turn, forces the compiler to generate a lot of non-vector code; in fact,
                OV estimates nearly a 3X speedup if it were fully vectorized. In contrast, note that OV portrays HACC,
                entirely in green - no chances for gain.  This, together with its very high efficiency
                (see Fig. bestcomp) indicates that it will scale well with many more cores.



                {' '}
                <Link className='link'
                    to="/qaas/overview/multiprocessor_comp_contents"
                > Click back  </Link>
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