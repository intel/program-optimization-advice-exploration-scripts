import React from 'react';
import { useNavigate } from 'react-router-dom'
import Button from '@mui/material/Button';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';



export default function ConstraintsAndScope() {
    const navigate = useNavigate();
    const navigateToHome = () => {
        navigate('/');
    };
    return (
        <div style={{ marginTop: 80 }}>
            <p>Our ambitious goals are constrained by practical, technical, and legal realities. Our broad scope includes: computer systems including HW architecture from 1 processor to small MP systems (100+) cores,
                big-core/small-core systems and GPUs, a range of compilers and languages across various application domains (chemistry, physics, engineering, weather, etc.)
                and multiple algorithmic approaches per domain. So, there are millions of possible combinations, whose impracticality forces us to make choices.
                Furthermore, not all computations are equally measurable, technically limiting us. Other combinations are closed, enforcing legal/practical constraints on probing the details of HW/SW systems.
            </p>

            <p>

                Across the CQ scope, some comparisons are uninteresting; they show negligible differences. We focus on wider swings in computational quality on popular HW/SW configurations,
                to illustrate the potential benefits of our approach. Meaningful results arise when large Q variations appear for what seem to be small parametric changes in measurable variables.
                Besides performance, we show power consumption (operating cost) and reliability variations. System buyers and app developers generally want high performance,
                broadly useful, reliable systems, and we touch on all.

            </p>

            <p>

                At any phase of history, one finds market surges that focus narrowly on one topic or another. Today, AI is king, in the 1990 – 2000 era personal computing boomed, HPC arose in the 70s – 90s, etc. Across these sometimes-frenzied periods, little changes conceptually; CQ stays the same but $ volumes and pricing margins surge and recede, as the general purpose/special
                purpose balances vary. Thus, we do not attempt to evaluate effectiveness/cost, because in
                frenzied times, buyers may pay more for features, and suppliers happily raise their margins.

            </p>




            <Button sx={{ ml: 3 }} variant="contained" onClick={navigateToHome} endIcon={<ArrowForwardIcon />}>Go back</Button>

        </div>
    );
}