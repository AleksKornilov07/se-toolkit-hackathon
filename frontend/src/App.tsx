import { useState, useEffect } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import axios from 'axios'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Item {
  id: number
  name: string
  url: string
  current_price: number
  is_active: boolean
}

interface PriceHistory {
  checked_at: string
  price: number
}

interface AIAnalysis {
  current_price: number
  avg_price: number
  min_price: number
  max_price: number
  trend: string
  recommendation: string
  reason: string
  data_points: number
}

function App() {
  const [items, setItems] = useState<Item[]>([])
  const [selectedItem, setSelectedItem] = useState<Item | null>(null)
  const [history, setHistory] = useState<PriceHistory[]>([])
  const [newUrl, setNewUrl] = useState('')
  const [newName, setNewName] = useState('')
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const userId = 1

  useEffect(() => {
    fetchItems()
  }, [])

  const fetchItems = async () => {
    const res = await axios.get(`${API_URL}/api/items/`, {
      params: { user_id: userId },
    })
    setItems(res.data)
  }

  const fetchHistory = async (itemId: number) => {
    const res = await axios.get(`${API_URL}/api/items/${itemId}/history`)
    setHistory(res.data)
    setSelectedItem(items.find(i => i.id === itemId) || null)
    setAiAnalysis(null)
  }

  const fetchAIAnalysis = async (itemId: number) => {
    setLoading(true)
    try {
      const res = await axios.get(`${API_URL}/api/ai/analyze/${itemId}`)
      setAiAnalysis(res.data)
    } catch {
      setAiAnalysis(null)
    }
    setLoading(false)
  }

  const seedMockData = async (itemId: number) => {
    await axios.post(`${API_URL}/api/ai/seed/${itemId}`)
    fetchHistory(itemId)
    fetchAIAnalysis(itemId)
  }

  const addItem = async () => {
    if (!newUrl) return
    await axios.post(`${API_URL}/api/items/?user_id=${userId}`, {
      name: newName || 'Product',
      url: newUrl,
      store: 'generic',
    })
    setNewUrl('')
    setNewName('')
    fetchItems()
  }

  const deleteItem = async (id: number) => {
    await axios.delete(`${API_URL}/api/items/${id}`)
    if (selectedItem?.id === id) {
      setSelectedItem(null)
      setHistory([])
      setAiAnalysis(null)
    }
    fetchItems()
  }

  const chartData = {
    labels: history.map((h) => new Date(h.checked_at).toLocaleDateString()),
    datasets: [
      {
        label: 'Price ($)',
        data: history.map((h) => h.price),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.3,
        fill: true,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' as const },
      title: { display: true, text: 'Price History' },
    },
  }

  return (
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto', fontFamily: 'system-ui' }}>
      <h1>📦 PriceTracker</h1>
      <p style={{ color: '#666' }}>Track product prices and get AI-powered buy/wait recommendations</p>

      <div style={{ background: '#f5f5f5', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
        <h3>Add New Item</h3>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <input type="text" placeholder="Product name" value={newName} onChange={(e) => setNewName(e.target.value)} style={{ padding: '8px', flex: 1, minWidth: '200px' }} />
          <input type="text" placeholder="Product URL" value={newUrl} onChange={(e) => setNewUrl(e.target.value)} style={{ padding: '8px', flex: 2, minWidth: '300px' }} />
          <button onClick={addItem} style={{ padding: '8px 16px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Add Item</button>
        </div>
      </div>

      <h2>Your Items ({items.length})</h2>
      {items.length === 0 ? (
        <p style={{ color: '#666' }}>No tracked items yet. Add one above!</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {items.map((item) => (
            <li key={item.id} style={{ padding: '12px', marginBottom: '8px', background: item.is_active ? '#f0f9ff' : '#f5f5f5', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <strong>{item.name}</strong><br />
                <span style={{ color: '#666', fontSize: '0.9em' }}>${item.current_price} | {item.store}</span>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button onClick={() => { fetchHistory(item.id); seedMockData(item.id); }} style={{ padding: '6px 12px', background: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>View Chart</button>
                <button onClick={() => deleteItem(item.id)} style={{ padding: '6px 12px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Delete</button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {selectedItem && history.length > 0 && (
        <div style={{ marginTop: '30px' }}>
          <h2>Price History: {selectedItem.name}</h2>
          <Line data={chartData} options={chartOptions} />
          <div style={{ marginTop: '20px' }}>
            <button onClick={() => fetchAIAnalysis(selectedItem.id)} disabled={loading} style={{ padding: '10px 20px', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: '6px', cursor: loading ? 'not-allowed' : 'pointer', fontSize: '16px' }}>
              {loading ? 'Analyzing...' : '🤖 AI: Buy or Wait?'}
            </button>
          </div>
          {aiAnalysis && (
            <div style={{ marginTop: '16px', padding: '16px', background: aiAnalysis.recommendation === 'BUY NOW' ? '#dcfce7' : '#fef3c7', borderRadius: '8px', border: `2px solid ${aiAnalysis.recommendation === 'BUY NOW' ? '#22c55e' : '#f59e0b'}` }}>
              <h3 style={{ margin: '0 0 8px 0' }}>{aiAnalysis.recommendation === 'BUY NOW' ? '✅ BUY NOW' : '⏳ WAIT'}</h3>
              <p style={{ margin: '4px 0' }}>{aiAnalysis.reason}</p>
              <div style={{ display: 'flex', gap: '16px', marginTop: '8px', fontSize: '14px', color: '#666' }}>
                <span>Avg: ${aiAnalysis.avg_price}</span>
                <span>Min: ${aiAnalysis.min_price}</span>
                <span>Max: ${aiAnalysis.max_price}</span>
                <span>Trend: {aiAnalysis.trend}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {selectedItem && history.length === 0 && (
        <div style={{ marginTop: '30px', padding: '20px', background: '#fffbeb', borderRadius: '8px' }}>
          <p>⏳ No price history yet. The scheduler checks prices every 15 minutes.</p>
          <button onClick={() => seedMockData(selectedItem.id)} style={{ padding: '8px 16px', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '8px' }}>🎲 Generate Demo Data</button>
        </div>
      )}
    </div>
  )
}

export default App
