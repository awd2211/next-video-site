import { Outlet } from 'react-router-dom'
import Header from '../Header'
import Footer from '../Footer'

const Layout = () => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white">
      <Header />
      <main 
        className="flex-1 container mx-auto px-4 py-8" 
        role="main"
        id="main-content"
        tabIndex={-1}
      >
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}

export default Layout
