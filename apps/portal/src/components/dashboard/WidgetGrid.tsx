'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, GripVertical, Maximize2, Minimize2 } from 'lucide-react';
import { useWidgetStore, type WidgetType } from '@/store/useWidgetStore';

// Widget components
import WeatherWidget from '@/components/widgets/WeatherWidget';
import CryptoWidget from '@/components/widgets/CryptoWidget';
import NewsWidget from '@/components/widgets/NewsWidget';
import StocksWidget from '@/components/widgets/StocksWidget';
import TasksWidget from '@/components/widgets/TasksWidget';
import ClockWidget from '@/components/widgets/ClockWidget';
import AIChatWidget from '@/components/widgets/AIChatWidget';

const WIDGET_COMPONENTS: Record<WidgetType, React.FC> = {
    weather: WeatherWidget,
    crypto: CryptoWidget,
    news: NewsWidget,
    stocks: StocksWidget,
    'ai-chat': AIChatWidget,
    tasks: TasksWidget,
    clock: ClockWidget,
    calendar: () => <div className="text-xs text-white/30 font-mono text-center">Calendar — Coming Soon</div>,
};

const SIZE_CLASSES = {
    small: 'col-span-1 row-span-1',
    medium: 'col-span-1 row-span-1 md:col-span-1',
    large: 'col-span-1 md:col-span-2 row-span-1',
};

export default function WidgetGrid() {
    const widgets = useWidgetStore((s) => s.widgets);
    const editMode = useWidgetStore((s) => s.editMode);
    const removeWidget = useWidgetStore((s) => s.removeWidget);
    const resizeWidget = useWidgetStore((s) => s.resizeWidget);

    const enabledWidgets = widgets.filter((w) => w.enabled);

    if (enabledWidgets.length === 0) {
        return (
            <div className="flex items-center justify-center py-12">
                <p className="text-xs font-mono text-white/20">
                    No widgets active. Click &quot;+ Add Widget&quot; to get started.
                </p>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
            <AnimatePresence mode="popLayout">
                {enabledWidgets
                    .sort((a, b) => a.position - b.position)
                    .map((widget) => {
                        const WidgetComponent = WIDGET_COMPONENTS[widget.type];
                        if (!WidgetComponent) return null;

                        return (
                            <motion.div
                                key={widget.id}
                                layout
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
                                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                                className={`relative group ${SIZE_CLASSES[widget.size]}`}
                            >
                                <div className={`
                                    h-full min-h-[180px] p-4 rounded-xl
                                    bg-white/[0.03] backdrop-blur-sm
                                    border transition-all duration-300
                                    ${editMode
                                        ? 'border-cyan-500/30 shadow-[0_0_15px_rgba(0,243,255,0.1)]'
                                        : 'border-white/[0.06] hover:border-white/[0.12]'
                                    }
                                `}>
                                    {/* Edit mode controls */}
                                    {editMode && (
                                        <div className="absolute top-2 right-2 z-20 flex items-center gap-1">
                                            <button
                                                onClick={() => {
                                                    const sizes = ['small', 'medium', 'large'] as const;
                                                    const current = sizes.indexOf(widget.size);
                                                    const next = sizes[(current + 1) % sizes.length];
                                                    resizeWidget(widget.id, next);
                                                }}
                                                className="p-1 bg-black/40 rounded hover:bg-white/10 transition-colors"
                                                title="Resize"
                                            >
                                                {widget.size === 'large' ? (
                                                    <Minimize2 className="w-3 h-3 text-white/40" />
                                                ) : (
                                                    <Maximize2 className="w-3 h-3 text-white/40" />
                                                )}
                                            </button>
                                            <button
                                                onClick={() => removeWidget(widget.id)}
                                                className="p-1 bg-black/40 rounded hover:bg-red-500/20 transition-colors"
                                                title="Remove widget"
                                            >
                                                <X className="w-3 h-3 text-white/40 hover:text-red-400" />
                                            </button>
                                        </div>
                                    )}

                                    {/* Drag handle (edit mode) */}
                                    {editMode && (
                                        <div className="absolute top-2 left-2 z-20 cursor-grab active:cursor-grabbing">
                                            <GripVertical className="w-3.5 h-3.5 text-white/20" />
                                        </div>
                                    )}

                                    {/* Widget content */}
                                    <WidgetComponent />
                                </div>
                            </motion.div>
                        );
                    })}
            </AnimatePresence>
        </div>
    );
}
