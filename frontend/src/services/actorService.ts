import api from './api'

export interface Actor {
  id: number
  name: string
  avatar: string | null
  biography: string | null
  birth_date: string | null
  country_id: number | null
  created_at: string
}

export interface ActorDetail extends Actor {
  videos: any[]
}

export interface PaginatedActors {
  total: number
  page: number
  page_size: number
  items: Actor[]
}

export const actorService = {
  // 获取演员列表
  getActors: async (
    page: number = 1,
    pageSize: number = 20,
    search: string = ''
  ): Promise<PaginatedActors> => {
    const response = await api.get('/actors/', {
      params: { page, page_size: pageSize, search }
    })
    return response.data
  },

  // 获取演员详情
  getActor: async (actorId: number): Promise<ActorDetail> => {
    const response = await api.get(`/actors/${actorId}`)
    return response.data
  },

  // 获取演员参演的视频
  getActorVideos: async (
    actorId: number,
    page: number = 1,
    pageSize: number = 20
  ): Promise<any> => {
    const response = await api.get(`/actors/${actorId}/videos`, {
      params: { page, page_size: pageSize }
    })
    return response.data
  }
}
