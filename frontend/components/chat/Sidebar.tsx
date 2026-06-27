import React from "react";
import { MessageSquare, Settings, Plus, LayoutGrid, Trash2 } from "lucide-react";
import { api } from "@/lib/api";

export function Sidebar({ 
  onNewChat, 
  onLoadChat,
  history, 
  setHistory 
}: { 
  onNewChat?: () => void;
  onLoadChat?: (id: string) => void;
  history: {id: string, title: string}[];
  setHistory: (h: {id: string, title: string}[]) => void;
}) {

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await api.deleteConversation(id);
      const newHistory = history.filter(item => item.id !== id);
      setHistory(newHistory);
    } catch (error) {
      console.error("Failed to delete conversation", error);
    }
  };

  return (
    <div className="flex h-full w-[280px] flex-col border-r border-slate-200/60 bg-white/40 backdrop-blur-xl p-5 shadow-[4px_0_24px_rgb(0,0,0,0.02)] shrink-0">
      <button 
        onClick={onNewChat}
        className="flex w-full items-center justify-center gap-2 rounded-2xl bg-white border border-slate-200 p-3 text-sm font-semibold text-slate-700 shadow-sm transition-all hover:border-blue-200 hover:bg-blue-50/50 hover:text-blue-600 mb-8 hover:shadow-md"
      >
        <Plus className="h-5 w-5" />
        Nuevo Chat
      </button>

      <div className="flex-1 overflow-y-auto">
        <div className="text-[11px] font-bold tracking-wider text-slate-400 mb-4 px-2">
          HISTORIAL
        </div>
        <div className="flex flex-col gap-1">
          {history.length === 0 && (
            <div className="text-xs text-slate-400 px-2 italic">No hay chats recientes</div>
          )}
          {history.map((item) => (
            <div 
              key={item.id} 
              onClick={() => onLoadChat && onLoadChat(item.id)}
              className="group flex w-full items-center gap-3 rounded-xl py-2 px-3 text-sm font-medium text-slate-600 transition-colors hover:bg-white hover:shadow-sm cursor-pointer"
            >
              <MessageSquare className="h-4 w-4 shrink-0 text-slate-400 group-hover:text-blue-500 transition-colors" />
              <div className="flex-1 text-left truncate group-hover:text-blue-600">
                {item.title}
              </div>
              <button 
                onClick={(e) => handleDelete(e, item.id)}
                className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-50 hover:text-red-500 rounded-md transition-all text-slate-400"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          ))}
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
