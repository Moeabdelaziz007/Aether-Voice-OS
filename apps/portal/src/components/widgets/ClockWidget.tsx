'use client';

import React, { useState, useEffect } from 'react';

export default function ClockWidget() {
    const [time, setTime] = useState(new Date());

    useEffect(() => {
        const interval = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(interval);
    }, []);

    const hours = time.getHours().toString().padStart(2, '0');
    const minutes = time.getMinutes().toString().padStart(2, '0');
    const seconds = time.getSeconds().toString().padStart(2, '0');

    return (
        <div className="flex flex-col items-center justify-center h-full">
            {/* Time display */}
            <div className="flex items-baseline gap-1 font-mono">
                <span className="text-3xl font-light text-white/90">{hours}</span>
                <span className="text-xl text-white/20 animate-pulse">:</span>
                <span className="text-3xl font-light text-white/90">{minutes}</span>
                <span className="text-lg text-white/30 ml-1">{seconds}</span>
            </div>

            {/* Date */}
            <div className="text-[10px] font-mono text-white/20 mt-2 tracking-wider uppercase">
                {time.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
            </div>
        </div>
    );
}
