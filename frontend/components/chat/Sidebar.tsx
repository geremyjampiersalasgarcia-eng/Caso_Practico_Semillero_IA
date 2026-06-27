import React from "react";
import { MessageSquare, Settings, Plus, LayoutGrid } from "lucide-react";

export function Sidebar() {
  return (
    <div className="flex h-full w-[280px] flex-col border-r border-slate-200/60 bg-white/40 backdrop-blur-xl p-5 shadow-[4px_0_24px_rgb(0,0,0,0.02)]">
      <button className="flex w-full items-center justify-center gap-2 rounded-2xl bg-white border border-slate-200 p-3 text-sm font-semibold text-slate-700 shadow-sm transition-all hover:border-blue-200 hover:bg-blue-50/50 hover:text-blue-600 mb-8 hover:shadow-md">
        <Plus className="h-5 w-5" />
        Nuevo Chat
      </button>

      <div className="flex-1 overflow-y-auto">
        <div className="text-[11px] font-bold tracking-wider text-slate-400 mb-4 px-2">
          HISTORIAL
        </div>
        <div className="flex flex-col gap-1">
          {/* Mock history items */}
          <button className="group flex w-full items-center gap-3 rounded-xl py-2.5 px-3 text-sm font-medium text-slate-600 transition-colors hover:bg-white hover:shadow-sm hover:text-blue-600">
            <MessageSquare className="h-4 w-4 shrink-0 text-slate-400 group-hover:text-blue-500 transition-colors" />
            <span className="truncate">¿Cómo configuro la BD?</span>
          </button>
          <button className="group flex w-full items-center gap-3 rounded-xl py-2.5 px-3 text-sm font-medium text-slate-600 transition-colors hover:bg-white hover:shadow-sm hover:text-blue-600">
            <MessageSquare className="h-4 w-4 shrink-0 text-slate-400 group-hover:text-blue-500 transition-colors" />
            <span className="truncate">Error en el despliegue</span>
          </button>
        </div>
      </div>

      <div className="pt-4 border-t border-slate-200/60 mt-auto space-y-1">
        <button className="flex w-full items-center gap-3 rounded-xl py-2.5 px-3 text-sm font-medium text-slate-600 transition-colors hover:bg-white hover:shadow-sm">
          <LayoutGrid className="h-4 w-4 shrink-0 text-slate-400" />
          Dashboard
        </button>
        <button className="flex w-full items-center gap-3 rounded-xl py-2.5 px-3 text-sm font-medium text-slate-600 transition-colors hover:bg-white hover:shadow-sm">
          <Settings className="h-4 w-4 shrink-0 text-slate-400" />
          Configuración
        </button>
      </div>
    </div>
  );
}
