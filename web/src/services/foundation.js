import api from './api'
export async function allRecords(path, signal) {
  let result = [], page
  do {
    page = (await api.get(path, { params: { skip: result.length, limit: 500 }, signal })).data
    result.push(...page)
  } while (page.length === 500)
  return result
}
export const errorMessage = error => {
  const detail = error.response?.data?.detail
  return typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map(e => e.msg).join('; ') : 'The service could not be reached. Your saved records have not been changed.'
}
export const amount = value => Number(value).toLocaleString('en-KE', { maximumFractionDigits: 2 })
export const displayTime = value => value ? new Date(/[Zz]|[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`).toLocaleString('en-KE', { timeZone: 'Africa/Nairobi', dateStyle: 'medium', timeStyle: 'short' }) : 'Not recorded'
