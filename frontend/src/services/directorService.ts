import api from './api'

export interface Director {
  id: number
  name: string
  avatar: string | null
  biography: string | null
  birth_date: string | null
  country_id: number | null
  created_at: string
}

export interface DirectorDetail extends Director {
  videos: any[]
}

export interface PaginatedDirectors {
  total: number
  page: number
  page_size: number
  items: Director[]
}

export const directorService = {
  // 获取导演列表
  getDirectors: async (
    page: number = 1,
    pageSize: number = 20,
    search: string = ''
  ): Promise<PaginatedDirectors> => {
    const response = await api.get('/directors/', {
      params: { page, page_size: pageSize, search }
    })
    return response.data
  },

  // 获取导演详情
  getDirector: async (directorId: number): Promise<DirectorDetail> => {
    const response = await api.get(`/directors/${directorId}`)
    return response.data
  },

  // 获取导演执导的视频
  getDirectorVideos: async (
    directorId: number,
    page: number = 1,
    pageSize: number = 20
  ): Promise<any> => {
    const response = await api.get(`/directors/${directorId}/videos`, {
      params: { page, page_size: pageSize }
    })
    return response.data
  }
}
