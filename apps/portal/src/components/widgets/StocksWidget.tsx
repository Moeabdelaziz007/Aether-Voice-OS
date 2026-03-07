'use client';

import React, { useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StockItem {
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
}

const MOCK_STOCKS: StockItem[] = [
    { symbol: 'AAPL', name: 'Apple', price: 245.80, change: 3.20, changePercent: 1.32 },
    { symbol: 'GOOGL', name: 'Alphabet', price: 198.45, change: -1.15, changePercent: -0.58 },
    { symbol: 'NVDA', name: 'NVIDIA', price: 1024.60, change: 28.40, changePercent: 2.85 },
    { symbol: 'MSFT', name: 'Microsoft', price: 478.90, change: 5.60, changePercent: 1.18 },
];

export default function StocksWidget() {
    const [stocks] = useState<StockItem[]>(MOCK_STOCKS);

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono text-white/30 uppercase tracking-widest">Markets</span>
                <span className="text-[10px] font-mono text-white/20">US Markets</span>
            </div>

            {/* Stocks list */}
            <div className="flex flex-col gap-2">
                {stocks.map((stock) => {
                    const isPositive = stock.change >= 0;
                    const changeColor = isPositive ? 'text-emerald-400' : 'text-red-400';
                    const changeBg = isPositive ? 'bg-emerald-500/10' : 'bg-red-500/10';

                    return (
                        <div key={stock.symbol} className="flex items-center gap-3 py-1.5">
                            <div className="w-10">
                                <div className="text-xs font-mono text-white/70 font-medium">{stock.symbol}</div>
                            </div>
                            <div className="flex-1 text-xs text-white/30 truncate">{stock.name}</div>
                            <div className="text-xs font-mono text-white/60 text-right">
                                ${stock.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                            </div>
                            <div className={`flex items-center gap-1 text-xs font-mono px-2 py-0.5 rounded ${changeBg} ${changeColor}`}>
                                {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                {isPositive ? '+' : ''}{stock.changePercent.toFixed(2)}%
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
