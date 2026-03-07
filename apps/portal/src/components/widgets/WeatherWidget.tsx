'use client';

import React, { useState, useEffect } from 'react';
import { Cloud, Droplets, Wind, Sun, CloudRain, CloudSnow, CloudLightning } from 'lucide-react';

interface WeatherData {
    city: string;
    temp: number;
    condition: string;
    humidity: number;
    wind: number;
    feelsLike: number;
}

const MOCK_WEATHER: WeatherData = {
    city: 'San Francisco',
    temp: 18,
    condition: 'Partly Cloudy',
    humidity: 65,
    wind: 12,
    feelsLike: 16,
};

const CONDITION_ICONS: Record<string, React.ReactNode> = {
    'Sunny': <Sun className="w-8 h-8 text-amber-400" />,
    'Partly Cloudy': <Cloud className="w-8 h-8 text-cyan-300" />,
    'Rainy': <CloudRain className="w-8 h-8 text-blue-400" />,
    'Snowy': <CloudSnow className="w-8 h-8 text-white/80" />,
    'Stormy': <CloudLightning className="w-8 h-8 text-yellow-400" />,
};

export default function WeatherWidget() {
    const [weather, setWeather] = useState<WeatherData>(MOCK_WEATHER);
    const [time, setTime] = useState(new Date());

    useEffect(() => {
        const interval = setInterval(() => setTime(new Date()), 60000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono text-white/30 uppercase tracking-widest">Weather</span>
                <span className="text-[10px] font-mono text-white/20">
                    {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
            </div>

            {/* Main temp + condition */}
            <div className="flex items-center gap-4 mb-4">
                {CONDITION_ICONS[weather.condition] || <Cloud className="w-8 h-8 text-white/40" />}
                <div>
                    <div className="text-3xl font-light text-white/90 leading-none">
                        {weather.temp}°
                    </div>
                    <div className="text-xs text-white/40 mt-1">{weather.condition}</div>
                </div>
            </div>

            {/* Details grid */}
            <div className="grid grid-cols-3 gap-2 mt-auto">
                <div className="bg-white/[0.03] rounded-lg p-2 border border-white/5">
                    <Droplets className="w-3 h-3 text-cyan-400/60 mb-1" />
                    <div className="text-xs font-mono text-white/60">{weather.humidity}%</div>
                    <div className="text-[9px] text-white/20">Humidity</div>
                </div>
                <div className="bg-white/[0.03] rounded-lg p-2 border border-white/5">
                    <Wind className="w-3 h-3 text-cyan-400/60 mb-1" />
                    <div className="text-xs font-mono text-white/60">{weather.wind} km/h</div>
                    <div className="text-[9px] text-white/20">Wind</div>
                </div>
                <div className="bg-white/[0.03] rounded-lg p-2 border border-white/5">
                    <Sun className="w-3 h-3 text-amber-400/60 mb-1" />
                    <div className="text-xs font-mono text-white/60">{weather.feelsLike}°</div>
                    <div className="text-[9px] text-white/20">Feels</div>
                </div>
            </div>

            {/* City */}
            <div className="mt-3 text-[10px] font-mono text-white/20 text-right">
                📍 {weather.city}
            </div>
        </div>
    );
}
