import React from 'react';

import bestcompImage from '../imgs/bestcomp.png';

export default function Multiprocessor() {
    return (
        <div className="textPageContainer">
            <h1>C1.3 Multiprocessing</h1>
            <h2>Introduction</h2>
            <p>
                QaaS covers multiprocessing (MP) in the form of both throughput and parallelism, but only in the HPC context of getting one problem solved.
                It does not deal with many-problem throughput (which is usually the domain of cost, job scheduling  and OS management).
                We discuss two broad topics: compilation 1.1 and scalability, separately and in that order.
            </p>

            <p>
                Fig. bestcomp shows MP performance due to computer technology – HW/compiler -- per app, Uniform output across histogram views using colors and 1 or 2 labels.
            </p>
            <div className='imageContainer'>
                <img src={bestcompImage} alt="BestComp Description" />
            </div>





        </div>
    );


}