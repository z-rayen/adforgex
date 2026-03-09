import { createContext, useContext, useState, ReactNode } from 'react';
import { AuthUser } from '../types';

interface AuthContextValue {
    user: AuthUser | null;
    token: string | null;
    login: (token: string, user: AuthUser) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue>({
    user: null,
    token: null,
    login: () => { },
    logout: () => { },
    isAuthenticated: false,
});

export function AuthProvider({ children }: { children: ReactNode }) {
    const [token, setToken] = useState<string | null>(() => localStorage.getItem('adforge_token'));
    const [user, setUser] = useState<AuthUser | null>(() => {
        const raw = localStorage.getItem('adforge_user');
        return raw ? JSON.parse(raw) : null;
    });

    const login = (t: string, u: AuthUser) => {
        localStorage.setItem('adforge_token', t);
        localStorage.setItem('adforge_user', JSON.stringify(u));
        setToken(t);
        setUser(u);
    };

    const logout = () => {
        localStorage.removeItem('adforge_token');
        localStorage.removeItem('adforge_user');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
