import { useEffect, useState } from 'react';
import { Activity, Hand } from 'lucide-react';

interface GestureData {
  type: string;
  label: string;
  confidence: number;
}

interface ControllerData {
  mode: string;
  triggered: boolean;
  progress: number;
  message: string;
}

interface DetectionData {
  hands_detected: number;
  gestures: GestureData[];
  controller?: ControllerData;
}

const DetectionInfo = ({ cameraId }: { cameraId: number }) => {
  const [data, setData] = useState<DetectionData | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/api/v1/cameras/${cameraId}/ws/detection`);

    ws.onopen = () => setIsConnected(true);
    ws.onerror = () => console.log('WS Error');
    ws.onclose = () => setIsConnected(false);
    
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        setData(message);
      } catch (e) {
        console.error("Error parsing WS message", e);
      }
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [cameraId]);

  return (
    <div className="bg-industrial-gray p-6 rounded-xl border border-gray-700 h-full flex flex-col shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Activity size={20} className="text-accent-blue" />
          Live Detection
        </h3>
        <div className={`px-3 py-1 rounded-lg text-xs font-mono border ${
          isConnected 
            ? 'bg-green-500/20 text-green-400 border-green-500/30' 
            : 'bg-red-500/20 text-red-400 border-red-500/30'
        }`}>
          {isConnected ? '● CONNECTED' : '○ OFFLINE'}
        </div>
      </div>

      {/* SEKCJA KONTROLERA (STATUS SYSTEMU) */}
      {data?.controller && (
        <div className="mb-6 bg-black/30 p-4 rounded-lg border border-gray-700">
          <div className="flex justify-between mb-3 text-xs uppercase font-bold tracking-wider">
            <span className="text-gray-400">Mode:</span>
            <span className={`px-2 py-0.5 rounded ${
              data.controller.mode === 'safe' ? 'bg-yellow-500/20 text-yellow-400' :
              data.controller.mode === 'all' ? 'bg-green-500/20 text-green-400' :
              'bg-blue-500/20 text-accent-blue'
            }`}>
              {data.controller.mode.toUpperCase()}
            </span>
          </div>
          
          {/* Pasek Postępu (Safe Mode) */}
          {data.controller.mode === 'safe' && (
            <div className="mb-3">
              <div className="w-full bg-gray-700 h-4 rounded-full overflow-hidden border border-gray-600">
                <div 
                  className={`h-full transition-all duration-100 ease-linear flex items-center justify-center text-[10px] font-bold ${
                    data.controller.triggered ? 'bg-success-green' : 'bg-yellow-500'
                  }`}
                  style={{ width: `${data.controller.progress * 100}%` }}
                >
                  {data.controller.progress > 0.2 && `${Math.round(data.controller.progress * 100)}%`}
                </div>
              </div>
            </div>
          )}

          {/* Status wiadomość */}
          <div className={`text-center font-mono text-sm font-bold p-2 rounded ${
            data.controller.triggered 
              ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
              : 'bg-gray-800/50 text-gray-400'
          }`}>
            {data.controller.message || '---'}
          </div>
        </div>
      )}

      {/* LISTA WYKRYTYCH GESTÓW */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {!data || data.hands_detected === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 py-12">
            <Hand size={64} className="mb-4 opacity-10" />
            <p className="text-sm">No hands detected</p>
            <p className="text-xs text-gray-600 mt-2">Show your hand to the camera</p>
          </div>
        ) : (
          <div className="space-y-4">
            {data.gestures.map((gesture, idx) => (
              <div key={idx} className="bg-gray-800 p-4 rounded-lg border-l-4 border-accent-blue shadow-md transition-all hover:bg-gray-750">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
                      {gesture.type} Hand
                    </span>
                    <h4 className="text-xl font-bold text-white mt-1 tracking-tight">
                      {gesture.label}
                    </h4>
                  </div>
                  <div className="text-right">
                    <div className={`text-3xl font-bold ${
                      gesture.confidence > 0.8 ? 'text-green-400' : 
                      gesture.confidence > 0.5 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {(gesture.confidence * 100).toFixed(0)}%
                    </div>
                    <span className="text-[9px] text-gray-500 uppercase">Confidence</span>
                  </div>
                </div>
                
                {/* Pasek pewności */}
                <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-300 ${
                      gesture.confidence > 0.8 ? 'bg-green-500' : 
                      gesture.confidence > 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${gesture.confidence * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DetectionInfo;
