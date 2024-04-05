import React from 'react';

import { Link } from 'react-router-dom';

export default function Miniapps() {
    return (
        <div className="textPageContainer">
            <h1>C1.1.1 Miniapps</h1>
            <p>
                The overall QaaS results for 7 miniapps run on
                {' '}
                <Link
                    to="/system_config/ice_lake"
                > Intel Ice Lake  </Link>
                {' '}
                and
                {' '}
                <Link
                    to="/system_config/sapphire_rapids"
                > SPR  </Link>
                {' '}
                are discussed here; first the best compiler,
                then the benefits of QaaS are explained. The best compiler per miniapp is simply the compiler for which QaaS found a
                flag setting whose performance beat all others; 48 compilation cases were tested – the 3 compilers above with16 flag
                settings each. Fig. bestcomp shows that all 3 compilers are necessary in this multi-compilation result, with ICX winning on Miniqmc,
                while GCC and ICX win in 2 other cases, each. The 2 tie cases have times within 10% of each other on all 3 compilers.
                [Comd shifted gcc was only kripke - need to align explanation with deeper compiler graphs showing ICC clear best]
            </p>


            <p>
                From 16 to 48 cores per code were used to obtain total Gf and Gf/core exceedimg an efficiency threshold of 50% on this ICL system.
                For more details about MP performance runs see
                {' '}
                <Link
                    to="/cq_overview_multiprocessor"

                > C1.3 Multiprocessor</Link>

                . For more details about these codes and their compilation, see C 1 1 1 A or B? Need notation.
            </p>

            <h2>Compilation</h2>

            <p>
                Here, a baseline compiler suggested by the developer or chosen by QaaS experts is compared with 16 or15 other QaaS runs.
                For these 7 miniapps, the QaaS benefits can be summarized (see Table appgain), as 2 ties, and various numbers of codes
                with up to more than 4X performance gains for the C++ version of Cloverleaf.


            </p>

            <p>
                At a high level, ISVs and multi-app developers, or CSPs and computer managers, are mostly interested in compiler choice outcomes
                based on performance gains, measured in numbers of codes. There are practical subtleties here; Fig. bestcomp shows the best performing compiler,
                but what if two compilers produce performances that are 10% apart but far better than the third? As Fig. appgain makes clear,
                some gains are large enough to build in compiler choice tolerance, in the interest of avoiding recompilation
                and perhaps maintaining a minimal set of compiler on a CSP site. These topics are taken up below.

            </p>

            <p>
                For more details about the wins and losses of each compiler,
                see Section
                {' '}
                <Link to="/compiler_details"> C.1.1.1 A </Link>
                {' '}
                or continue to
                {' '}
                <Link to="/apps">C.1.1.2 </Link>
                {' '}
                for similar discussions about applications.
            </p>


            <p>
                Level 3 insert Everyone read and put in comments. This is where we can show the total benefits of QaaS and use as much detail as we wishl.
                Since it cuts across  many topics, the nature of the pointer system we are using, allows us to point from various places: compilers, MP,
                languages if we have a section, etc..
            </p>

            <p>
                Oct 12 Relative to 3.1.where we compare miniapps vs. compilers and architectures, the major driver of difference lies not in compilers or architectures,
                but in the structures of the codes themselves. On the one hand HACC (a cosmology code) computes on large dense matrices [can we check this - OV?HM:
                I think OV exposes an array access efficiency metric that may help discriminate between AMG and HACC], whereas AMG (a multigrid solver)
                has sparse data structures that become effectively smaller due to the multiple grid sizing of the algorithm. So for this pair,
                extreme data structure differences drive the order of magnitude performance differences. What about data size differences
                [as far as memory foot print is used a proxy to estimate data size, AMG due to replication can exhaust memory capacity and
                saturate memory bandwidth. HACC is more compute-bound]? Vector lengths and number of efficiently useful cores both matter
                (note that HACC strong scaling parallelism uses 48 while AMG is a hybrid (?32MPI, 1 OMP) using 32 cores.
            </p>

            <p>
                Many good compilers have strong abilities to respond to code structural nuances, but differences in cost models and specific
                transformation capabilities allow the manifestation of various performance levels.
            </p>

            <p>
                Another driver of performance differences is the source language used and its relation to various compilers.
                Cloverleaf (a hydrodynamics code), yields about 2X the Gf/core performance in C++ as in Fortran, and 4X in total Gf,
                because the C++ version runs efficiently on 32 cores, while Fortran uses only 16. Need more words explaining why this is true?
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