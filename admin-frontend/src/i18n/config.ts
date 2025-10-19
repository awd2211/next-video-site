import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import zhCN from './locales/zh-CN.json';
import enUS from './locales/en-US.json';
import zhTW from './locales/zh-TW.json';
import jaJP from './locales/ja-JP.json';
import deDE from './locales/de-DE.json';
import frFR from './locales/fr-FR.json';

i18n.use(initReactI18next).init({
  resources: {
    'zh-CN': { translation: zhCN },
    'en-US': { translation: enUS },
    'zh-TW': { translation: zhTW },
    'ja-JP': { translation: jaJP },
    'de-DE': { translation: deDE },
    'fr-FR': { translation: frFR },
  },
  lng: localStorage.getItem('admin_language') || 'zh-CN',
  fallbackLng: 'zh-CN',
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;


