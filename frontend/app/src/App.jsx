import { useEffect, useState } from 'react'
import './App.css'

// в dev запросы /api проксирует vite, в prod nginx.
const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

function ProductImage({ product }) {
  const [failed, setFailed] = useState(false)

  if (!product.image_url || failed) {
    return (
      <div className="card-placeholder" aria-hidden="true">
        {product.name.slice(0, 1).toUpperCase()}
      </div>
    )
  }

  return (
    <img
      src={product.image_url}
      alt={product.name}
      loading="lazy"
      onError={() => setFailed(true)}
    />
  )
}

function ProductCard({ product }) {
  return (
    <article className="card">
      <div className="card-image">
        <ProductImage product={product} />
      </div>
      <div className="card-body">
        <h2>{product.name}</h2>
        <span className="card-key">{product.image_key}</span>
        {product.created_at && (
          <time className="card-date" dateTime={product.created_at}>
            {new Date(product.created_at).toLocaleDateString('ru-RU')}
          </time>
        )}
      </div>
    </article>
  )
}

export default function App() {
  const [products, setProducts] = useState([])
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [requestId, setRequestId] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    fetch(`${API_BASE}/`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`API вернул HTTP ${response.status}`)
        }
        return response.json()
      })
      .then((data) => {
        setProducts(data)
        setStatus('ready')
      })
      .catch((reason) => {
        if (reason.name === 'AbortError') {
          return
        }
        setError(reason.message)
        setStatus('error')
      })

    return () => controller.abort()
  }, [requestId])

  function handleRetry() {
    setStatus('loading')
    setError(null)
    setRequestId((value) => value + 1)
  }

  return (
    <div className="page">
      <header className="hero">
        <p className="eyebrow">INVIX</p>
        <h1>Каталог товаров</h1>
        <p>
          Витрина минyи-приложения
        </p>
      </header>

      <section className="catalog">
        {status === 'loading' && (
          <p className="status" role="status">
            Загружаем каталог…
          </p>
        )}

        {status === 'error' && (
          <div className="notice" role="alert">
            <strong>Каталог временно недоступен.</strong>
            <span>{error}</span>
            <button type="button" onClick={handleRetry}>
              Повторить
            </button>
          </div>
        )}

        {status === 'ready' && products.length === 0 && (
          <div className="notice">
            <strong>Пока пусто.</strong>
            <span>Добавьте первый товар через POST /product/.</span>
          </div>
        )}

        {status === 'ready' && products.length > 0 && (
          <div className="grid" aria-label="Товары">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>

      <footer className="footer">
        <span>FastAPI</span>
        <span>PostgreSQL</span>
        <span>MinIO</span>
        <span>Telegram Mini App</span>
      </footer>
    </div>
  )
}
