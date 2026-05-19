import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    return Promise.reject(error)
  },
)

export default api
