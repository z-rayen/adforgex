import React from 'react';
import styles from './Card.module.css';

interface CardProps {
    title: string;
    icon: string;
    children: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ title, icon, children }) => {
    return (
        <div className={styles.card}>
            <div className={styles.cardTitle}>
                <span className={styles.sn}>{icon}</span> {title}
            </div>
            {children}
        </div>
    );
};

export default Card;
