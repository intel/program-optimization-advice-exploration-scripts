import React from 'react';
import MPperfImage from '../imgs/MPperf.png';
import ArccompHistogram from '../graph/histogram/ArccompHistogram';
import MpratioTable from '../graph/table/MpratioTable';
import MulticorePerfGFlopsLineGraph from '../graph/line/MulticorePerfGFlopsLineGraph';
export default function MultiprocessorPerfContents() {
    return (
        <div className="textPageContainer">
            <ArccompHistogram />

            <h1>Multiprocessor performance comparisons </h1>

            <p>
                Here we introduce the multicore or multiprocessor systems (MP) architectural and software complexities beyond the unicore discussion above.
                Next, we compare MP performance for well-compiled codes (as determined above).

                MP performance involves more programming choices (OMP, MPI)
                as well as architecture choices (# cores, # sockets and # nodes). Here we use all three QaaS views in a plot of perf vs. codes, a histogram
                of architecture performance differences, and an overview table outlining the many diverse aspects of these runs.
            </p>

            <p>
                Fig. MPperf shows plots of Gf/core for ICL and SPR 2-socket MP systems vs. the 7 miniapps, annotated with the best/worst system perf ratio shown in
                the color of the winner (see legend). Fig. arcomp

                shows that HACC Gf/core is 1.2- 1.5 faster on ICL than SPR, while Miniquc is 1.1 – 1.2 faster on SPR.
                Table mpratio lists MP performance differences and many of their contributing factors. At this point, we merely list the details; understanding them
                requires probing this website more deeply. A main takeaway is to observe the diversity of optimal cases for these 7 simple miniapps (randomly chosen from the web).
            </p>

            <div className='multiple-graph-container'>
                <MulticorePerfGFlopsLineGraph />

                <MpratioTable />

            </div>
            <p>
                First, we can see a 40X range of best total Gf, and nearly that (27X) in Gf/core. The number of cores used per code (for Ep &gt; .5) ranges over 3X on ICL and 4X on SPR,
                and 1.33 per system (per code). The various numbers of cores used per code reflects both architectural and SW effects. We can see that the use of OMP and MPI scaling
                replication factors vary and that pinning for affinity also varies substantially.
            </p>

            <p>
                In each case, QaaS chooses parameter values for best performance, so the variations imply potential difficulties that human developers will encounter
                in balancing these factors per code on each machine. Developers who use “consensus” defaults obtained by word of mouth, web searches, or intuition,
                can be misled and incur various kinds of performance degradation. Automated searches eventually seem necessary for naïve developers and even experts;
                for the latter, searches can at least provide validation for expertly configured computations.
            </p>





        </div>
    );


}