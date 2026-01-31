import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [email, setEmail] = useState('demo@example.com')
  const [password, setPassword] = useState('demo123')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    if (!email || !password) {
      setError('Email and password are required')
      return
    }

    try {
      setLoading(true)
      // Placeholder auth: integrate your backend endpoint here
      await new Promise((r) => setTimeout(r, 400))
      login('demo-token')
      // success animation then navigate
      setSuccess(true)
      setTimeout(() => navigate('/home', { replace: true }), 700)
    } catch (err) {
      setError('Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen relative flex items-center justify-center bg-black text-white overflow-hidden">
      <div className="login-grid"></div>
      <div className="login-blob w-72 h-72 bg-emerald-600/40 top-[-40px] left-[-40px] animate-float-slow"></div>
      <div className="login-blob w-72 h-72 bg-blue-600/40 bottom-[-40px] right-[-40px] animate-float-slow" style={{ animationDelay: '1.2s' }}></div>
      {/* Snowfall */}
      <div className="snowflakes" aria-hidden>
        {Array.from({ length: 30 }).map((_, i) => (
          <span key={i} style={{ left: `${Math.random()*100}%`, animationDuration: `${6 + Math.random()*6}s`, animationDelay: `${Math.random()*3}s` }}>❄</span>
        ))}
      </div>
      <div className="w-full max-w-md bg-zinc-900/60 border border-zinc-800 rounded-2xl p-8 shadow-2xl animate-tilt-in backdrop-blur">
        <h1 className="text-3xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-emerald-200">Sign in</h1>
        <p className="text-sm text-zinc-400 mb-6">Welcome back to Talk with Database</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="field">
            <label className="block text-sm mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg bg-zinc-900/60 border border-emerald-500/30 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              placeholder="you@example.com"
              autoComplete="email"
            />
          </div>
          <div className="field">
            <label className="block text-sm mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg bg-zinc-900/60 border border-emerald-500/30 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </div>
          {error && (
            <div className="text-red-400 text-sm">{error}</div>
          )}
          <button
            type="submit"
            className="w-full bg-emerald-600/90 hover:bg-emerald-500 transition-all rounded-lg py-3 font-medium disabled:opacity-60 shadow-lg shadow-emerald-600/20"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
      {success && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-emerald-400 text-6xl" style={{ transform: 'scale(0.9)', animation: 'pop 700ms ease-out forwards' }}>✔</div>
        </div>
      )}
    </div>
  )
}
