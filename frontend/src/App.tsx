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

function App() {
  const [items, setItems] = useState<Item[]>([])
  const [selectedItem, setSelectedItem] = useState<Item | null>(null)
  const [history, setHistory] = useState<PriceHistory[]>([])
  const [newUrl, setNewUrl] = useState('')
  const [newName, setNewName] = useState('')
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
    }
    fetchItems()
  }

  const chartData = {
    labels: history.map((h) => new Date(h.checked_at).toLocaleString()),
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
      <p style={{ color: '#666' }}>Track product prices and get notified when they drop</p>

      <div
        style={{
          background: '#f5f5f5',
          padding: '16px',
          borderRadius: '8px',
          marginBottom: '20px',
        }}
      >
        <h3>Add New Item</h3>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <input
            type="text"
            placeholder="Product name (optional)"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            style={{ padding: '8px', flex: 1, minWidth: '200px' }}
          />
          <input
            type="text"
            placeholder="Product URL"
            value={newUrl}
            onChange={(e) => setNewUrl(e.target.value)}
            style={{ padding: '8px', flex: 2, minWidth: '300px' }}
          />
          <button
            onClick={addItem}
            style={{
              padding: '8px 16px',
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Add Item
          </button>
        </div>
      </div>

      <h2>Your Items ({items.length})</h2>
      {items.length === 0 ? (
        <p style={{ color: '#666' }}>No tracked items yet. Add one above!</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {items.map((item) => (
            <li
              key={item.id}
              style={{
                padding: '12px',
                marginBottom: '8px',
                background: item.is_active ? '#f0f9ff' : '#f5f5f5',
                borderRadius: '6px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <strong>{item.name}</strong>
                <br />
                <span style={{ color: '#666', fontSize: '0.9em' }}>
                  ${item.current_price} | {item.store}
                </span>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => {
                    setSelectedItem(item)
                    fetchHistory(item.id)
                  }}
                  style={{
                    padding: '6px 12px',
                    background: '#10b981',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  View Chart
                </button>
                <button
                  onClick={() => deleteItem(item.id)}
                  style={{
                    padding: '6px 12px',
                    background: '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {selectedItem && history.length > 0 && (
        <div style={{ marginTop: '30px' }}>
          <h2>Price History: {selectedItem.name}</h2>
          <Line data={chartData} options={chartOptions} />
        </div>
      )}

      {selectedItem && history.length === 0 && (
        <div style={{ marginTop: '30px', padding: '20px', background: '#fffbeb', borderRadius: '8px' }}>
          <p>⏳ No price history yet. The scheduler will check prices every 5 minutes.</p>
        </div>
      )}
    </div>
  )
}

export default App
