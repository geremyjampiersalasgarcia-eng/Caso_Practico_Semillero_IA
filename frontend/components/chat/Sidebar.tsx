import React from "react";
import { MessageSquare, Settings, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function Sidebar() {
  return (
    <div className="flex h-full w-[260px] flex-col border-r bg-muted/20 p-4">
      <Button variant="default" className="w-full justify-start gap-2 mb-6">
        <PlusCircle className="h-4 w-4" />
        Nuevo Chat
      </Button>

      <div className="flex-1 overflow-y-auto">
        <div className="text-xs font-semibold text-muted-foreground mb-4">
          HISTORIAL
        </div>
        <div className="flex flex-col gap-2">
          {/* Mock history items */}
          <Button variant="ghost" className="w-full justify-start gap-2 h-auto py-2 px-3 font-normal text-sm">
            <MessageSquare className="h-4 w-4 shrink-0 text-muted-foreground" />
            <span className="truncate">¿Cómo configuro la base de datos?</span>
          </Button>
          <Button variant="ghost" className="w-full justify-start gap-2 h-auto py-2 px-3 font-normal text-sm">
            <MessageSquare className="h-4 w-4 shrink-0 text-muted-foreground" />
            <span className="truncate">Error en el despliegue</span>
          </Button>
        </div>
      </div>

      <div className="pt-4 border-t mt-auto">
        <Button variant="ghost" className="w-full justify-start gap-2">
          <Settings className="h-4 w-4" />
          Configuración
        </Button>
      </div>
    </div>
  );
}
