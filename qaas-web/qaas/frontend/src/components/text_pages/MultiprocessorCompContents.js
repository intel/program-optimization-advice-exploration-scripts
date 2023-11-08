import React from 'react';
import BestCompTable from '../graph/table/BestcompTable';
import AppgainHistogram from '../graph/histogram/AppgainHistogram';
export default function MultiprocessorCompContents() {
    return (
        <div className="textPageContainer">
            <h1>Multiprocessor comparisons of 3 compilers</h1>
            <p>

                Three current compiler leaders – Intel ICX and ICC plus GCC (and their Fortran versions) were used here for the same 7 miniapps as the unicore runs.
                In Fig. appgain, another standard QaaS view – a histogram – shows the spread of performance gains over a good default compiler flag setting for runs
                in Intel Ice Lake. Here, QaaS searches among 16 optimizing flag combinations per compiler to find the best. The gains range from more than 4X to nothing;
                we define a tie as &lt; 10% gain, but the slider bar can be used to adjust this. For example, in some cases, a 5% gain may be valued.


            </p>
            <p>
                Table bestcomp summarizes key points about these miniapps, their performance, and the maximum number of cores for which efficiency Ep &gt; .5
                (where Ep =t1/p tp) – in table bestcomp,  the Ep threshold is adjustable [Yue]. It is interesting and typical to see the diversity of performance,
                winning compilers, and total cores usable efficiently. It is noteworthy that AMG is a multigrid solver with data access difficulties leading to poor
                relatively poor performance and low compiler differentiation. On the other hand, HACC is easily parallelizable and vectorizable so it runs well
                everywhere with little need for compiler excellence.
            </p>
            <p>
                Fig. bestcomp also repeats the ICL Gf column from Table unicore perf. The ratio (Gfuni)/(GfMP/core) varies from 1.3 for HACC to 2.95 for Cloverleaf++.
                Because MP computations contain extra parallelization instructions, this is reasonable. Since HACC has high parallel efficiency we can expect a low ratio,
                and Cloverleaf++, as a C++ code, seems to have extra parallelism overhead instructions. CHECK details it is a good oppy to discuss parallel ohd.
            </p>

            <AppgainHistogram />
            <h2>
                Fig Appgain
            </h2>

            <BestCompTable />
            <h2>
                Fig Bestcomp
            </h2>



        </div>
    );


}