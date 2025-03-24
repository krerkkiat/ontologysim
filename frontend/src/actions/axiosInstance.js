import axios from "axios";

/**
 * creating axios instance with baseURL
 */
export const axiosInstance = axios.create({baseURL: import.meta.env.ONTOLOGYSIM_API_BASEURL,withCredentials:true,    
    
  })