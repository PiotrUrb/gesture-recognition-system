import { useEffect, useRef } from 'react';

interface VideoPlayerProps {
  cameraId: number;
}

const VideoPlayer = ({ cameraId }: VideoPlayerProps) => {
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    if (!imgRef.current) return;

    const streamUrl = `http://localhost:8000/api/v1/cameras/${cameraId}/stream`;
    imgRef.current.src = streamUrl;

    return () => {
      if (imgRef.current) {
        imgRef.current.src = '';
      }
    };
  }, [cameraId]);

  return (
    <div className="relative w-full h-full bg-gray-900 rounded-lg overflow-hidden">
      <img
        ref={imgRef}
        alt="Camera Feed"
        className="w-full h-full object-contain"
        style={{
          imageRendering: 'auto',
          willChange: 'contents'
        }}
      />
      
      {/* Overlay info */}
      <div className="absolute top-2 left-2 bg-black/50 px-2 py-1 rounded text-xs text-white">
        Camera {cameraId}
      </div>
    </div>
  );
};

export default VideoPlayer;
