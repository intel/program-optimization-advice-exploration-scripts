import React from 'react';
import BestCompTable from '../../graph/table/BestcompTable';
import AppgainHistogram from '../../graph/histogram/AppgainHistogram';
import { Link } from 'react-router-dom';
import TooltipComponent from '../../TooltipComponent';
import { InlineMath, BlockMath } from 'react-katex';
import { useHighlightNavigation } from '../../hooks/useHighlightNavigation';

export default function MultiprocessorCompContents() {
    const efficiencyFormula = "E_c = \\frac{T_1}{c \\times T_c}";
    useHighlightNavigation();

    return (
        <div className="textPageContainer">
            <h1>Compiler Comparison</h1>

            <p>

                Three current compiler leaders – Intel ICX and ICC plus GCC (and their Fortran versions) were used here for the multicore runs of the same 7 miniapps as the unicore runs of Fig. utab.
                See 
                {' '}
                <Link className='def-link'
                    to="/system_config"
                >compiler version numbers</Link>
                {' '}
                here.
                {' '}<Link className='link'
                    to="/qaas/overview/compiler_comparison#figappgain"
                >Fig. appgain</Link>{' '}
                is another standard QaaS view (histogram)
                showing the spread of performance gains found by QaaS over a good baseline default compiler
                flag setting for Intel Ice Lake runs. Here, QaaS searches among 16 optimizing flag
                combinations per compiler to find the best performance gain over the baseline.

                The gains range from nothing to more than 4X; we define a performance tie (by default) as &lt; 10% gain,
                but the slider bar can be used to adjust this. For example, in some use cases, a 5% gain
                may be judged as significant.
                <AppgainHistogram />

            </p>



            <p>


                    <Link className='link'
                        to="/qaas/overview/compiler_comparison#figbestcomp"
                    > Fig. bestcomp</Link> {' '} summarizes key points about these miniapp runs. First, we can see the 40X per code range for best total Gf (see last row),
                and nearly that (27X) for Gf/core. Also shown is the maximum number of cores for which
                {' '}
                <TooltipComponent id="efficiency-formula" content={
                    <BlockMath>
                        {efficiencyFormula}
                    </BlockMath>
                }>
                    efficiency
                </TooltipComponent>
                {' '}


                Ec &gt; .5 (ranging from 16 to 48 cores). 
                {' '}
                <Link className='link'
                        to="/qaas/overview/compiler_comparison#figbestcomp"
                    >Fig. bestcomp</Link>,{' '}
                 the Ec threshold is adjustable [Yue]. It is interesting and typical to
                see the diversity of performance, winning compilers, and total cores usable efficiently. As examples, AMG is an algebraic multigrid solver
                with data access difficulties leading to relatively poor performance and low compiler differentiation. On the other hand,
                HACC (an n-body cosmology code) is easily parallelizable and vectorizable so it runs well everywhere with little need for compiler excellence.
                See

                <Link className='footnote-link'
                    to="/qaas/overview/AMG_HACC_click_target"
                > details about AMG and HACC  </Link>
                here.
            </p>

            <p>
            <Link className='link'
                        to="/qaas/overview/compiler_comparison#figbestcomp"
                    > Fig. bestcomp</Link> {' '} includes several performance metrics: the Ice Lake Gf column (from Fig. utab) leads to the ratio
                (Gf uni)/(Gf MC/core) [ADD], which varies from 1.3 for HACC to 2.95 for Cloverleaf++. This is reasonable because
                MC computations contain extra parallelization instructions, and must share L3 cache. Since HACC has high parallel
                efficiency we can expect a low ratio, and Cloverleaf++, as a C++ code, seems to have extra parallelism overhead
                instructions. <span className="check-color">CHECK details it is a good oppy to discuss parallel ohd.</span>
            </p>


            <BestCompTable />

            <p>
                In this section, we assumed that the application developers had not thought about best compiler settings,
                so we started with generally good default flags. In many cases, app developers do make recommendations
                based on their own studies of selected compilers per architecture. See here 

                {' '}
                <Link className='footnote-link'
                    to="/qaas/overview/developer_flag_recommendations"
                >an evaluation of developer flag recommendations</Link>.
            </p>




        </div>
    );


}