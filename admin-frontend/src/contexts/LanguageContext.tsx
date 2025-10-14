import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import i18n from '../i18n/config';

type Language = 'zh-CN' | 'en-US';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('admin_language') as Language;
    return saved || 'zh-CN';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('admin_language', lang);
    localStorage.setItem('language', lang); // 同步到主语言设置
    i18n.changeLanguage(lang); // 切换 i18next 语言
  };

  useEffect(() => {
    // 同步语言设置
    localStorage.setItem('language', language);
    i18n.changeLanguage(language);
  }, [language]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
