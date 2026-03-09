"use client";

import React from 'react';
import { Cpu } from 'lucide-react';

interface Props {
    selectedModel: string;
    apiKey: string;
    updateDNA: (data: any) => void;
}

const MODELS = ['Google Gemini 2.5', 'OpenAI GPT-4o', 'Anthropic Claude 3.5', 'Local Llama 3'];

export default function BrainStep({ selectedModel, apiKey, updateDNA }: Props) {
    return (
        <div className="space-y-8">
            <h2 className="text-3xl font-black tracking-tighter uppercase text-white/90">Intelligence Matrix</h2>
            <div className="grid grid-cols-2 gap-4">
                {MODELS.map((brain) => (
                    <button
                        key={brain}
                        onClick={() => updateDNA({ model: brain })}
                        className={`p-6 rounded-3xl border text-left transition-all ${selectedModel === brain
                                ? 'bg-cyan-500/10 border-cyan-500 text-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.1)]'
                                : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'
                            }`}
                    >
                        <Cpu className={`w-6 h-6 mb-4 ${selectedModel === brain ? 'text-cyan-400' : 'text-white/20'}`} />
                        <div className="font-bold text-sm tracking-tight">{brain}</div>
                        <div className="text-[10px] opacity-60 uppercase tracking-widest mt-1">Neural Backbone</div>
                    </button>
                ))}
            </div>
            <div className="space-y-4">
                <label className="text-[10px] font-black text-white/30 uppercase tracking-[0.3em]">
                    Secure API Key Entry
                </label>
                <input
                    type="password"
                    placeholder="Paste Key Here..."
                    value={apiKey}
                    onChange={(e) => updateDNA({ apiKey: e.target.value })}
                    className="w-full bg-black/40 border border-white/10 rounded-2xl py-4 px-6 focus:border-cyan-500/50 focus:outline-none transition-all text-white/80 font-mono text-sm"
                />
            </div>
        </div>
    );
}
