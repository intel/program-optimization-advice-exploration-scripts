import React from 'react';
import MPsysImage from '../imgs/MPsys.png';

export default function TypeOfScaling() {
    return (
        <div className="textPageContainer">
            <h1>C1.4.1.b Type of scaling – replication factors</h1>
            <p>
                The y-axis is perf Gf or FOM and x-axis shows replication factors from 1 (strong scaling) to p (throughput), with points for interesting variations
                (e.g. logarithmic) between – these hybrid or weak cases would show OMP vs MPI counts.
                Recall Jan documents laying this out in detail – also get scalability defs. for Definition bar.
            </p>
            <p>
                Fig. MPsys is another view of the four MP modes of operation, and their relations to each other. In short,
                parallelism and throughput are extreme differences of use, while hybrid mode combines the two.
            </p>
            <div className='imageContainer'>
                <img src={MPsysImage} alt="MPsysImage Description" />
            </div>
            <p>
                Fig. MPsys    The four modes of MP system operation
            </p>
            <p>
                Those 3 are variations on speeding up a single problem solution using an MP. Multiprogrammed systems are a distinct MP usage model,
                relying on shared HW to support a variety of distinct jobs.
            </p>

        </div>
    );


}