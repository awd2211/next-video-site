import { useTranslation } from 'react-i18next'

const Footer = () => {
  const { t } = useTranslation()
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-gray-800 border-t border-gray-700 mt-auto">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold text-red-600 mb-4">VideoSite</h3>
            <p className="text-gray-400">
              {t('footer.aboutDescription')}
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">{t('nav.categories')}</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="/category/movies" className="hover:text-white">{t('category.movie')}</a></li>
              <li><a href="/category/tv-series" className="hover:text-white">{t('category.tvSeries')}</a></li>
              <li><a href="/category/anime" className="hover:text-white">{t('category.anime')}</a></li>
              <li><a href="/category/documentary" className="hover:text-white">{t('category.documentary')}</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">{t('footer.support')}</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="/help" className="hover:text-white">{t('nav.help')}</a></li>
              <li><a href="/contact" className="hover:text-white">{t('nav.contact')}</a></li>
              <li><a href="/faq" className="hover:text-white">{t('nav.faq')}</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">{t('footer.legal')}</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="/privacy" className="hover:text-white">{t('nav.privacy')}</a></li>
              <li><a href="/terms" className="hover:text-white">{t('nav.terms')}</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
          <p>{t('footer.copyright', { year: currentYear })}</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
