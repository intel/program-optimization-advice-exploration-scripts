import React from 'react';

import bestcompImage from '../imgs/bestcomp.png';
import appGainImage from '../imgs/appgain.png';
import { Link } from 'react-router-dom';

export default function Miniapps() {
    return (
        <div className="textPageContainer">
            <h1>C1.1.1 Miniapps</h1>
            <p>
                The overall QaaS results for 7 miniapps run on Intel

                {' '}
                <Link
                    to="/system_config/ice_lake"

                > Ice Lake  </Link>
                {' '}

                (DKdecide how to include SKL and SPR, etc.)
                are discussed here; first the best compiler, then the benefits of QaaS are explained.
                The best compiler per miniapp is simply the compiler for which QaaS found a flag setting whose performance beat
                all others; 48 cases were tested – the 3 compilers above with16 flag settings each, see Fig. bestcomp.
                We can see that all 3 compilers are necessary in this multi-compilation result, with GCC winning on Kripke,
                while ICC and ICX win in 2 other cases, each. The 2 tie cases have times within 10% of each other on all 3 compilers.
            </p>
            <p>
                From 16 to 48 cores per code were used to obtain total Gf and Gf/core on this ICL system, to exceed an efficiency threshold of 50%.
                For more detail about MP performance runs see
                {' '}
                <Link
                    to="/cq_overview_multiprocessor"

                > C1.3 Multiprocessor</Link>

                . For more details about these codes and their compilation, see C 1 1 1 A or B? Need notation.
            </p>
            <div className='imageContainer'>
                <img src={bestcompImage} alt="BestComp Description" />
            </div>
            <h2>Compilation</h2>

            <p>
                At a high level, ISVs and multi-app developers, or CSPs and computer managers,
                are mostly interested in compiler choice outcomes based on performance gains,denominated in numbers of codes.
                Here, a baseline compiler suggested by the developer or chosen by QaaS experts is compared with all other QaaS runs.
                For these 7 miniapps, the QaaS benefits can be summarized (see Table appgain), as 2 ties,
                and various numbers of codes with up to more than 4X performance gains for the C++ version of Cloverleaf.


            </p>
            <div className='imageContainer'>
                <img src={appGainImage} alt="appGain Description" />
            </div>



            <p>
                For more details about the wins and losses of each compiler,
                see Section
                {' '}
                <Link
                    to="/multi_compiler_gains"

                >L2.1: Multi-Compiler Gains </Link>
                {' '}
                or continue to
                {' '}
                <Link to="/apps">C.1.1.2 </Link>
                {' '}
                for similar discussions about applications.
            </p>

            <h2>
                MP performance
            </h2>
            <p>
                Explain a bit about the runs on MP to get these numbers. And Gf columns.
            </p>
            <p>
                New table
            </p>





        </div>
    );


}