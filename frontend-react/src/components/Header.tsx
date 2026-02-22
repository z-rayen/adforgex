import React from 'react';
import styles from './Header.module.css';

const Header: React.FC = () => {
    return (
        <header className={styles.header}>
            <div className={styles.glow} />
            <div className={styles.inner}>
                <div className={styles.badge}>⚡ AI-Powered</div>
                <h1 className={styles.title}>
                    Ad<span className={styles.forge}>Forge</span>
                </h1>
                <p className={styles.subtitle}>
                    RAG · Vision · Scraper · 6-step pipeline — from product to high-conversion ad copy
                </p>
            </div>
        </header>
    );
};

export default Header;
