import React from 'react';
import MPperfImage from '../imgs/MPperf.png';
import ArccompHistogram from '../graph/histogram/ArccompHistogram';
import MpratioTable from '../graph/table/MpratioTable';
import MulticorePerfGFlopsLineGraph from '../graph/line/MulticorePerfGFlopsLineGraph';
import IntroLink from './IntroLink';
import { Link } from 'react-router-dom';
export default function MultiprocessorPerfContents() {
    return (
        <div className="textPageContainer">

            <h1>Multicore performance comparisons </h1>

            <p>
                Next we introduce multicore (MC) [or multiprocessor (MP)] system architectural and software complexities, beyond the unicore and compilation discussions above.
                We compare MC performance for well-compiled codes (as determined above).

                MC performance involves more programming choices (OMP, MPI) as well as architectural choices (# cores, # sockets and # nodes).
                Here we use all three QaaS views: a graph of performance vs. codes, a histogram of architectural performance differences,
                and an overview table outlining many diverse aspects of these runs.
            </p>
            <ArccompHistogram />



            <p>
                Fig. MPperf shows plots of Gf/core for ICL and SPR 2-socket MC systems vs. the 7 miniapps plus 4 whole applications,
                annotated with the best/worst system performance ratio shown in the color of the winner (see legend).
                Fig. arcomp is a histogram comparing ICL and SPR performance across the codes. It shows that HACC Gf/core is 1.2
                – 1.5 faster on ICL than SPR, while Miniqmc is 1.1 – 1.2 faster on SPR.
                Table mpratio lists MC performance differences and some of their contributing factors. The first column is the ICL Gf as seen earlier (Fig. Bestcomp),
                with a 40X range. From Fig. MPperf we know that all of the miniapps (except Kripke) are within 15% total Gf difference on SPR and ICL, and two of the whole apps have &gt; 15% performance differences.
                These differences shift and are somewhat larger for Gf/core.
            </p>
            <p>
                The number of cores used per code (for Ep &gt; .5) ranges over a factor of 3X on ICL and 4X on SPR. The last column offers architectural differences that affect these results:
                SPR uses a slower clock frequency for these runs, but uses 33% more cores on 3 codes. Cloverleaf F can use only ⅓ of the cores (pink) efficiently on either machine. However,
                3 of the 7 miniapps (green) use all cores available. Both x86 architectures use the same fraction of cores on each code.
                How much of the 40X performance range is attributable to high level HW parameters? The 1.33X core count of SPR is somewhat offset by its .79 clock frequency,
                but the 3X  range of core count/code is the largest effect shown. Despite the potential ~3X effect of all these factors, there remains an order of magnitude Gf differential across the codes.
                To explore this and fully explain the 40X total Gf range, requires understanding SW (including data structure and size) differences among the codes.
                At this point, we can merely present the  high level details above. A main takeaway is to observe some diversity in the optimal cases for these 7 simple miniapps (randomly chosen from the web).
                Highlights of the variations in HW/SW mismatches across these codes are further explored in BQI
                {' '}
                <Link className='link'
                    to="/qaas/overview"
                > click here</Link>
                .
                {' '}

            </p>


            <div className='multiple-graph-container'>
                <MulticorePerfGFlopsLineGraph />

                <MpratioTable />

            </div>




            <p>
                In each run, QaaS chooses parameter values for best performance, so the variations imply potential difficulties that human developers will encounter in balancing these factors per code on each machine.
                Developers who use “consensus” defaults obtained by word of mouth, web searches, or intuition, can be misled and incur various kinds of performance degradation. Automated searches eventually seem necessary
                for naïve developers and even experts; for the latter, searches can at least provide validation for expertly configured computations.web). A fuller understanding of these HW/SW mismatches requires probing
                this website more deeply.
            </p>




        </div>
    );


}