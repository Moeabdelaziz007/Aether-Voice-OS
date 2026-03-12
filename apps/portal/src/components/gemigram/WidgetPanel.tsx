'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { renderWidgets } from '@/services/widgets/registry';
import type { WidgetSpec } from '@/services/widgets/schema';
import { useAetherStore } from '@/store/useAetherStore';

/**
 * Dynamic widget panel that renders widgets from Gemini function calls
 */
export default function WidgetPanel() {
  const widgets = useAetherStore((s) => s.activeWidgets);
  const [displayedWidgets, setDisplayedWidgets] = useState<WidgetSpec[]>([]);

  useEffect(() => {
    // Convert store widgets to widget specs
    const specs = widgets.map((w) => ({
      id: w.id,
      type: w.type,
      props: w.props,
    })) as WidgetSpec[];
    setDisplayedWidgets(specs);
  }, [widgets]);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="h-14 border-b border-cyan-500/10 flex items-center">
        <h2 className="text-sm font-semibold text-gray-300">Dynamic Widgets</h2>
      </div>

      {/* Widget Grid */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <AnimatePresence mode="wait">
          {displayedWidgets.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full flex flex-col items-center justify-center text-gray-500 text-sm"
            >
              <svg className="w-12 h-12 mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.5a2 2 0 00-1 3.773A4.002 4.002 0 0013 15H9c-.666 0-1.274-.119-1.848-.336" />
              </svg>
              <p>No widgets yet</p>
              <p className="text-xs mt-2">Widgets will appear here when needed</p>
            </motion.div>
          ) : (
            displayedWidgets.map((widget, index) => (
              <motion.div
                key={widget.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ delay: index * 0.05 }}
              >
                {renderWidgets([widget])[0]}
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      {displayedWidgets.length > 0 && (
        <div className="h-12 border-t border-cyan-500/10 px-4 flex items-center justify-end gap-2">
          <button className="text-xs px-2 py-1 rounded hover:bg-black/60 transition-colors">
            Collapse All
          </button>
        </div>
      )}
    </div>
  );
}
