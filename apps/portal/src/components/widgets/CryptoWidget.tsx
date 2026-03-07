'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface CryptoItem {
    symbol: string;
    name: string;
    price: number;
    change24h: number;
    sparkline: number[];
}

const MOCK_CRYPTO: CryptoItem[] = [
    { symbol: 'BTC', name: 'Bitcoin', price: 97432.50, change24h: 2.34, sparkline: [94, 95, 93, 96, 95, 97, 97] },
    { symbol: 'ETH', name: 'Ethereum', price: 3847.20, change24h: -1.12, sparkline: [39, 38, 39, 38, 37, 38, 38] },
    { symbol: 'SOL', name: 'Solana', price: 198.45, change24h: 5.67, sparkline: [180, 185, 188, 192, 190, 195, 198] },
];

function MiniSparkline({ data, color }: { data: number[]; color: string }) {
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    const h = 24;
    const w = 60;
    const points = data.map((v, i) => {
        const x = (i / (data.length - 1)) * w;
        const y = h - ((v - min) / range) * h;
        return `${x},${y}`;
    }).join(' ');

    return (
        <svg width={w} height={h} className="opacity-60">
            <polyline fill="none" stroke={color} strokeWidth="1.5" points={points} />
        </svg>
    );
}

export default function CryptoWidget() {
    const [cryptos] = useState<CryptoItem[]>(MOCK_CRYPTO);

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono text-white/30 uppercase tracking-widest">Crypto</span>
                <span className="text-[10px] font-mono text-emerald-400/60">LIVE</span>
            </div>

            {/* Crypto list */}
            <div className="flex flex-col gap-2.5">
                {cryptos.map((coin) => {
                    const isPositive = coin.change24h >= 0;
                    const changeColor = isPositive ? 'text-emerald-400' : 'text-red-400';
                    const sparkColor = isPositive ? '#10B981' : '#F43F5E';

                    return (
                        <div key={coin.symbol} className="flex items-center gap-3 py-1.5">
                            {/* Symbol */}
                            <div className="w-8 h-8 rounded-lg bg-white/[0.05] border border-white/5 flex items-center justify-center text-xs font-mono text-white/60">
                                {coin.symbol.slice(0, 2)}
                            </div>

                            {/* Name + Price */}
                            <div className="flex-1 min-w-0">
                                <div className="text-sm text-white/80 font-medium">{coin.name}</div>
                                <div className="text-xs font-mono text-white/40">
                                    ${coin.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                </div>
                            </div>

                            {/* Sparkline */}
                            <MiniSparkline data={coin.sparkline} color={sparkColor} />

                            {/* Change */}
                            <div className={`flex items-center gap-0.5 text-xs font-mono ${changeColor}`}>
                                {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                {Math.abs(coin.change24h).toFixed(2)}%
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
