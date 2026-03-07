'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Plus, Check } from 'lucide-react';
import { useWidgetStore, WIDGET_CATALOG, type WidgetType } from '@/store/useWidgetStore';

export default function WidgetStoreModal() {
    const storeOpen = useWidgetStore((s) => s.storeOpen);
    const setStoreOpen = useWidgetStore((s) => s.setStoreOpen);
    const widgets = useWidgetStore((s) => s.widgets);
    const addWidget = useWidgetStore((s) => s.addWidget);
    const removeWidget = useWidgetStore((s) => s.removeWidget);

    const activeTypes = new Set(widgets.filter(w => w.enabled).map(w => w.type));

    if (!storeOpen) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-[60] flex items-center justify-center"
            >
                {/* Backdrop */}
                <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setStoreOpen(false)} />

                {/* Modal */}
                <motion.div
                    initial={{ scale: 0.95, y: 20 }}
                    animate={{ scale: 1, y: 0 }}
                    exit={{ scale: 0.95, y: 20 }}
                    className="relative z-10 w-full max-w-2xl mx-4 ultra-glass rounded-2xl border border-white/10 overflow-hidden"
                >
                    {/* Header */}
                    <div className="flex items-center justify-between px-6 py-4 border-b border-white/5">
                        <div>
                            <h2 className="text-lg font-medium text-white/90">Widget Store</h2>
                            <p className="text-xs text-white/30 font-mono mt-0.5">Add smart widgets to your dashboard</p>
                        </div>
                        <button
                            onClick={() => setStoreOpen(false)}
                            className="p-2 hover:bg-white/5 rounded-lg transition-colors"
                        >
                            <X className="w-4 h-4 text-white/40" />
                        </button>
                    </div>

                    {/* Widget catalog grid */}
                    <div className="p-6 grid grid-cols-2 md:grid-cols-4 gap-3 max-h-[60vh] overflow-y-auto">
                        {(Object.entries(WIDGET_CATALOG) as [WidgetType, typeof WIDGET_CATALOG[WidgetType]][]).map(([type, catalog]) => {
                            const isActive = activeTypes.has(type);
                            const activeWidget = widgets.find(w => w.type === type && w.enabled);

                            return (
                                <motion.button
                                    key={type}
                                    whileHover={{ scale: 1.03 }}
                                    whileTap={{ scale: 0.97 }}
                                    onClick={() => {
                                        if (isActive && activeWidget) {
                                            removeWidget(activeWidget.id);
                                        } else {
                                            addWidget(type);
                                        }
                                    }}
                                    className={`
                                        flex flex-col items-center gap-2 p-4 rounded-xl border transition-all
                                        ${isActive
                                            ? 'bg-cyan-500/10 border-cyan-500/30 shadow-[0_0_15px_rgba(0,243,255,0.1)]'
                                            : 'bg-white/[0.03] border-white/5 hover:border-white/15 hover:bg-white/[0.05]'
                                        }
                                    `}
                                >
                                    <span className="text-2xl">{catalog.icon}</span>
                                    <span className="text-xs font-medium text-white/70">{catalog.title}</span>
                                    <span className="text-[9px] text-white/30 text-center leading-tight">{catalog.description}</span>
                                    
                                    {/* Status indicator */}
                                    <div className={`mt-1 flex items-center gap-1 text-[9px] font-mono ${
                                        isActive ? 'text-cyan-400' : 'text-white/20'
                                    }`}>
                                        {isActive ? (
                                            <>
                                                <Check className="w-3 h-3" />
                                                Active
                                            </>
                                        ) : (
                                            <>
                                                <Plus className="w-3 h-3" />
                                                Add
                                            </>
                                        )}
                                    </div>
                                </motion.button>
                            );
                        })}
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}
