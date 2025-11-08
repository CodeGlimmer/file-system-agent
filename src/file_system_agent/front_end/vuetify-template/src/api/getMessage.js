import axios from 'axios'

const url = '/api/reply'

export const getMessage = async (message) => {
  return await axios.post(url, {
    content: message,
  })
}
