import React from 'react';

import bestcompImage from '../imgs/bestcomp.png';

export default function Multiprocessor() {
    return (
        <div className="textPageContainer">
            <h1>C1.3 Multiprocessor</h1>
            <p>
                Here we show MP performance due to computer technology – HW/compiler -- per app,
                Uniform output across histogram views using colors and 1 or 2 labels.

            </p>
            <div className='imageContainer'>
                <img src={bestcompImage} alt="BestComp Description" />
            </div>



        </div>
    );


}