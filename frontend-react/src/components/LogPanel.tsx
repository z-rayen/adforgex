import React, { useRef, useEffect } from 'react';
import styles from './LogPanel.module.css';
import { LogEntry } from '../types';

interface LogPanelProps {
    logs: LogEntry[];
}

const LogPanel: React.FC<LogPanelProps> = ({ logs }) => {
    const logRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (logRef.current) {
            logRef.current.scrollTop = logRef.current.scrollHeight;
        }
    }, [logs]);

    if (logs.length === 0) return null;

    return (
        <div ref={logRef} className={styles.logPanel}>
            {logs.map((log, index) => (
                <div key={index} className={styles.ll}>
                    <span className={styles.lt}>{log.timestamp}</span>
                    <span className={`${styles.lm} ${styles[log.level]}`}>{log.message}</span>
                </div>
            ))}
        </div>
    );
};

export default LogPanel;
