import React from 'react';

import bestcompImage from '../imgs/bestcomp.png';

export default function Multiprocessor() {
    return (
        <div className="textPageContainer">
            <h1>C1.3 Multiprocessor</h1>
            <h2>Introduction</h2>
            <p>
                Multiprocessing (MP) in the form of throughput and parallelism has a long history. QaaS covers aspects of each, but only in the HPC
                context of getting one problem solved, and not in the sense of many problem throughput (usually the domain of cost, job scheduling  and OS management).
                We consider two broad topics: compilation and scalability. They are discussed separately in that order.
            </p>
            <p>
                First, we show MP performance due to computer technology – HW/compiler -- per app, Uniform output across histogram views using colors and 1 or 2 labels.
                Add cores here and a bit more text for introducing a few details of compilation AND scaling.
            </p>

            <div className='imageContainer'>
                <img src={bestcompImage} alt="BestComp Description" />
            </div>



        </div>
    );


}