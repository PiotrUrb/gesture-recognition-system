import React, { useState } from 'react';
import { Camera, RefreshCw } from 'lucide-react';

interface VideoPlayerProps {
  cameraId: number;
  label?: string;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ cameraId, label }) => {
  const [key, setKey] = useState(0); // Służy do odświeżania obrazu (reconnect)
  const streamUrl = `http://localhost:8000/api/v1/cameras/${cameraId}/stream`;

  const handleRefresh = () => {
    setKey(prev => prev + 1); // Wymusza przeładowanie obrazka
  };

  return (
    <div className="bg-black rounded-xl overflow-hidden border border-gray-700 shadow-lg relative group">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/80 to-transparent p-4 flex justify-between items-center z-10 opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="flex items-center gap-2 text-white text-sm font-medium">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          LIVE - {label || `Camera ${cameraId}`}
        </div>
        <button 
          onClick={handleRefresh}
          className="p-2 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors"
          title="Reconnect stream"
        >
          <RefreshCw size={16} />
        </button>
      </div>

      {/* Video Stream */}
      <div className="aspect-video bg-gray-900 flex items-center justify-center relative">
        <img
          key={key} // Zmiana klucza przeładowuje img
          src={streamUrl}
          alt={`Camera ${cameraId} Stream`}
          className="w-full h-full object-cover"
          onError={(e) => {
            // Jeśli błąd ładowania (np. kamera offline), pokaż placeholder
            e.currentTarget.style.display = 'none';
            e.currentTarget.nextElementSibling?.classList.remove('hidden');
          }}
        />
        
        {/* Placeholder (gdy brak sygnału) */}
        <div className="hidden absolute inset-0 flex flex-col items-center justify-center text-gray-500">
          <Camera size={48} className="mb-2 opacity-50" />
          <p>No Signal</p>
          <button 
            onClick={handleRefresh} 
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition"
          >
            Retry Connection
          </button>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer;
