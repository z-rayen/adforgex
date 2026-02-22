import React from 'react';
import styles from './PipelineTracker.module.css';
import { StepStatus } from '../types';

interface PipelineTrackerProps {
    stepStatuses: Record<number, StepStatus>;
}

const steps = [
    { id: 1, label: 'S1: RAG+Analysis' },
    { id: 2, label: 'S2: Competitor' },
    { id: 3, label: 'S3: Images' },
    { id: 4, label: 'S4: Sentiment' },
    { id: 5, label: 'S5: Strategy' },
    { id: 6, label: 'S6: Ad Gen' },
];

const PipelineTracker: React.FC<PipelineTrackerProps> = ({ stepStatuses }) => {
    return (
        <div className={styles.card}>
            <div className={styles.cardTitle}>
                <span className={styles.sn}>⚡</span> Pipeline
            </div>
            <div className={styles.pipeTrack}>
                {steps.map((step, index) => (
                    <React.Fragment key={step.id}>
                        <div className={styles.ps}>
                            <div className={`${styles.psLabel} ${styles[stepStatuses[step.id]]}`}>
                                {step.label}
                            </div>
                        </div>
                        {index < steps.length - 1 && <div className={styles.psArrow}>→</div>}
                    </React.Fragment>
                ))}
            </div>
        </div>
    );
};

export default PipelineTracker;
