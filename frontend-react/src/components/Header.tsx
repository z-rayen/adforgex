import React from 'react';
import styles from './Header.module.css';

interface HeaderProps {
    serverUrl: string;
}

const Header: React.FC<HeaderProps> = ({ serverUrl }) => {
    return (
        <header className={styles.header}>
            <div className={styles.badge}>⚡ Full Stack</div>
            <h1 className={styles.title}>AdForge Pipeline</h1>
            <p className={styles.subtitle}>
                RAG + Playwright Scraper + Groq Vision + 6-step AI pipeline → high-conversion ad copy
            </p>
            <div className={styles.serverIndicator}>
                <span className={styles.dot}></span>
                Connected to backend at <span>{serverUrl}</span>
            </div>
        </header>
    );
};

export default Header;
