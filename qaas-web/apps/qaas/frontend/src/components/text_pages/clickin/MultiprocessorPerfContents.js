import React from 'react';
import ArccompHistogram from '../../graph/histogram/ArccompHistogram';
import MpratioTable from '../../graph/table/MpratioTable';
import MulticorePerfGFlopsLineGraph from '../../graph/line/MulticorePerfGFlopsLineGraph';
import { Link } from 'react-router-dom';
import { useHighlightNavigation } from '../../hooks/useHighlightNavigation';

export default function MultiprocessorPerfContents() {
    useHighlightNavigation();

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
                <Link className='link'
                    to="/qaas/overview/multicore_performance_comparisons#figmpperf"
                >Fig. MPperf</Link> {' '}
                shows plots of Gf/core for ICL and SPR 2-socket MC systems vs. the 7 miniapps plus 4 whole applications,
                annotated with the best/worst system performance ratio shown in the color of the winner (see legend).
                {' '} <Link className='link'
                    to="/qaas/overview/multicore_performance_comparisons#figarccomp"
                >Fig. Arccomp</Link> {' '}
                is a histogram comparing ICL and SPR performance across the codes. It shows that HACC Gf/core is 1.2
                – 1.5 faster on ICL than SPR, while Miniqmc is 1.1 – 1.2 faster on SPR.

                {' '} <Link className='link'
                    to="/qaas/overview/multicore_performance_comparisons#figmpratio"
                >Table mpratio</Link> {' '}
                lists MC performance differences and some of their contributing factors. The first column is the ICL Gf as seen earlier (Fig. Bestcomp),
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
                Highlights of the variations in HW/SW mismatches across these codes are further explored in BQI.

            </p>


            <div className='multiple-graph-container'>
                <MulticorePerfGFlopsLineGraph />

                <MpratioTable />

            </div>



            <div className='container-next-to-paragraph'>
                <p>Even top performance experts miss big gain opportunities. <br />
                    → QaaS helps everyone.</p>
            </div>

            <p>
                In each run, QaaS chooses parameter values for best performance, so the variations imply potential difficulties that human developers will encounter in balancing these factors per code on each machine.
                Developers who use “consensus” defaults obtained by word of mouth, web searches, or intuition, can be misled and incur various kinds of performance degradation. Automated searches eventually seem necessary
                for naïve developers and even experts; for the latter, searches can at least provide validation for expertly configured computations. A fuller understanding of these HW/SW mismatches requires probing
                this website more deeply.

                {' '}
                <Link className='link'
                    to="/qaas/cq_overview"
                >BQI</Link>
                {' '}
                gives more details about the multicore aspects of these codes. Otherwise you may return to the
                {' '}
                <Link className='link'
                    to="/overview"
                >introduction</Link>.
            </p>






        </div>
    );


}