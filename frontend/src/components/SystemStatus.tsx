import React, { useState, useEffect, useCallback, useRef } from 'react';
import { systemService } from '../services/systemService';

interface SystemStatusProps {
  onStatusChange?: (status: string) => void;
}

const SystemStatus: React.FC<SystemStatusProps> = ({ onStatusChange }) => {
  const [status, setStatus] = useState<string>('checking');
  const isInitialRender = useRef(true);

  const checkStatus = useCallback(async () => {
    try {
      const health = await systemService.checkHealth();
      setStatus(health.status);
      onStatusChange?.(health.status);
    } catch (error) {
      console.error('Status check failed:', error);
      setStatus('offline');
    }
  }, [onStatusChange]);

  // Initial check on mount
  useEffect(() => {
    if (isInitialRender.current) {
      isInitialRender.current = false;
      checkStatus();
    }
  }, [checkStatus]);

  // Poll status every 3 seconds
  useEffect(() => {
    const interval = setInterval(checkStatus, 3000);
    return () => clearInterval(interval);
  }, [checkStatus]);

  const getStatusColor = () => {
    switch (status) {
      case 'online':
        return 'bg-green-900/40 text-green-400 border-green-700/60';
      case 'offline':
        return 'bg-red-900/40 text-red-400 border-red-700/60';
      case 'checking':
        return 'bg-blue-900/40 text-blue-400 border-blue-700/60';
      default:
        return 'bg-gray-900/40 text-gray-400 border-gray-700/60';
    }
  };

  const getStatusDot = () => {
    switch (status) {
      case 'online':
        return '🟢';
      case 'offline':
        return '🔴';
      case 'checking':
        return '🔵';
      default:
        return '⚫';
    }
  };

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold tracking-wider transition-all ${getStatusColor()}`}>
      <span className="text-sm animate-pulse">{getStatusDot()}</span>
      <span>{status.toUpperCase()}</span>
    </div>
  );
};

export default SystemStatus;