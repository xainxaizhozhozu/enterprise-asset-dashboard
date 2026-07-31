import { useState, useCallback } from 'react'

/**
 * 通用 API 调用 hook，封装 loading / error / data 三态管理。
 *
 * 用法：
 *   const { data, loading, error, execute } = useApi(assetAPI.list)
 *   useEffect(() => { execute() }, [])
 *
 * execute() 接受与传入 apiFunc 相同的参数，返回 Promise<responseData>。
 * 调用方可以直接 .then() 链式处理，也可以只依赖 data 状态渲染。
 */
export default function useApi(apiFunc, { immediate = false, onSuccess, onError } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const execute = useCallback(async (...args) => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiFunc(...args)
      // axios 拦截器已解包 response.data；如果还有 .data 说明是原始响应
      const result = res?.data !== undefined ? res.data : res
      setData(result)
      onSuccess?.(result)
      return result
    } catch (err) {
      const msg = err?.detail || err?.response?.data?.detail || err?.message || '操作失败'
      setError(msg)
      onError?.(msg)
      throw err
    } finally {
      setLoading(false)
    }
  }, [apiFunc, onSuccess, onError])

  return { data, loading, error, execute, setData }
}
