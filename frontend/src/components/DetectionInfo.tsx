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
    timestamp: number;
    hands_detected: number;
    gestures: GestureData[];
    controller?: ControllerData;
}

const DetectionInfo = ({ cameraId }: { cameraId: number }) => {
    const [data, setData] = useState<DetectionData | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let ws: WebSocket | null = null;
        let reconnectTimeout: ReturnType<typeof setTimeout>;

        const connectWebSocket = () => {
            try {
                const wsUrl = `ws://localhost:8000/api/v1/cameras/${cameraId}/ws/detection`;
                console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);
                
                ws = new WebSocket(wsUrl);

                ws.onopen = () => {
                    console.log(`✅ WebSocket connected to camera ${cameraId}`);
                    setIsConnected(true);
                    setError(null);
                };

                ws.onerror = (event) => {
                    console.error(`❌ WebSocket error for camera ${cameraId}:`, event);
                    setError('Connection error');
                    setIsConnected(false);
                };

                ws.onclose = () => {
                    console.log(`❌ WebSocket closed for camera ${cameraId}`);
                    setIsConnected(false);
                    // Spróbuj ponownie połączyć za 3 sekundy
                    reconnectTimeout = setTimeout(connectWebSocket, 3000);
                };

                ws.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        setData(message);
                    } catch (e) {
                        console.error("❌ Error parsing WebSocket message:", e);
                    }
                };
            } catch (e) {
                console.error('❌ WebSocket connection error:', e);
                setError('Failed to connect');
                setIsConnected(false);
            }
        };

        connectWebSocket();

        return () => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.close();
            }
            if (reconnectTimeout) {
                clearTimeout(reconnectTimeout);
            }
        };
    }, [cameraId]);

    return (
        <div className="space-y-4">
            {/* STATUS */}
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Activity size={20} />
                    Live Detection
                </h3>
                <div className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-bold ${
                    isConnected ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'
                }`}>
                    <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></span>
                    {isConnected ? 'CONNECTED' : 'OFFLINE'}
                </div>
            </div>

            {/* ERROR MESSAGE */}
            {error && (
                <div className="p-3 bg-red-900/50 border border-red-500 rounded text-red-400 text-sm">
                    ⚠️ {error}
                </div>
            )}

            {/* SEKCJA KONTROLERA */}
            {data?.controller && (
                <div className="p-3 bg-gray-700 rounded-lg space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-gray-400 text-sm">Mode:</span>
                        <span className="font-bold text-blue-400 uppercase">{data.controller.mode}</span>
                    </div>

                    {data.controller.mode === 'safe' && data.controller.progress > 0 && (
                        <div className="space-y-1">
                            <div className="h-2 bg-gray-600 rounded-full overflow-hidden">
                                <div 
                                    className="h-full bg-blue-500 transition-all"
                                    style={{ width: `${data.controller.progress * 100}%` }}
                                ></div>
                            </div>
                            <span className="text-xs text-gray-400">
                                Progress: {Math.round(data.controller.progress * 100)}%
                            </span>
                        </div>
                    )}

                    {data.controller.message && (
                        <div className="text-sm text-yellow-400">
                            💬 {data.controller.message}
                        </div>
                    )}

                    {data.controller.triggered && (
                        <div className="p-2 bg-green-900 border border-green-500 rounded text-green-400 text-sm font-bold">
                            ✅ ACTION TRIGGERED!
                        </div>
                    )}
                </div>
            )}

            {/* LICZBA RĄKĄ */}
            <div className="p-3 bg-gray-700 rounded-lg">
                <div className="flex items-center gap-2 text-gray-400 text-sm">
                    <Hand size={16} />
                    <span>Hands detected: <span className="font-bold text-white">{data?.hands_detected || 0}</span></span>
                </div>
            </div>

            {/* GESTURES LIST */}
            <div className="space-y-2">
                {!data || data.hands_detected === 0 ? (
                    <div className="p-3 bg-gray-700 rounded-lg text-center text-gray-500 text-sm">
                        👋 No hands detected<br/>
                        <span className="text-xs">Show your hand to the camera</span>
                    </div>
                ) : (
                    data.gestures.map((gesture, idx) => (
                        <div key={idx} className="p-3 bg-gray-700 rounded-lg space-y-1">
                            <div className="flex items-center justify-between">
                                <div className="text-sm font-bold text-white">
                                    {gesture.type} Hand
                                </div>
                                <span className={`text-xs font-bold px-2 py-1 rounded ${
                                    gesture.confidence > 0.8 ? 'bg-green-900 text-green-400' :
                                    gesture.confidence > 0.5 ? 'bg-yellow-900 text-yellow-400' : 'bg-red-900 text-red-400'
                                }`}>
                                    {(gesture.confidence * 100).toFixed(0)}%
                                </span>
                            </div>
                            <div className="text-sm text-blue-400">{gesture.label}</div>
                            <div className="h-1 bg-gray-600 rounded-full overflow-hidden">
                                <div 
                                    className={`h-full transition-all ${
                                        gesture.confidence > 0.8 ? 'bg-green-500' :
                                        gesture.confidence > 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                                    }`}
                                    style={{ width: `${gesture.confidence * 100}%` }}
                                ></div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default DetectionInfo;