import api from './api'
import { Category, Country } from '@/types'

export const dataService = {
  getCategories: async (): Promise<Category[]> => {
    const response = await api.get('/categories')
    return response.data
  },

  getCountries: async (): Promise<Country[]> => {
    const response = await api.get('/countries')
    return response.data
  },
}
