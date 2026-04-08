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

const API_URL = ''

function App() {
  const [userId, setUserId] = useState(() => localStorage.getItem('pt_user_id') || '')
  const [loggedIn, setLoggedIn] = useState(false)
  const [items, setItems] = useState([])
  const [selectedItem, setSelectedItem] = useState(null)
  const [history, setHistory] = useState([])
  const [newUrl, setNewUrl] = useState('')
  const [newName, setNewName] = useState('')
  const [targetPrice, setTargetPrice] = useState('')
  const [aiAnalysis, setAiAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [editTarget, setEditTarget] = useState('')

  useEffect(() => {
    if (loggedIn && userId) fetchItems()
  }, [loggedIn, userId])

  useEffect(() => {
    if (userId && userId.trim() !== '') setLoggedIn(true)
  }, [])

  const handleLogin = () => {
    if (!userId.trim()) return
    localStorage.setItem('pt_user_id', userId)
    setLoggedIn(true)
    fetchItems()
  }

  const handleLogout = () => {
    localStorage.removeItem('pt_user_id')
    setUserId('')
    setLoggedIn(false)
    setItems([])
    setSelectedItem(null)
    setHistory([])
    setAiAnalysis(null)
  }

  const fetchItems = async () => {
    try {
      const res = await axios.get(API_URL + '/api/items/', { params: { user_id: Number(userId) } })
      setItems(res.data)
    } catch (e) { console.error('Fetch error:', e) }
  }

  const fetchHistory = async (itemId) => {
    const res = await axios.get(API_URL + '/api/items/' + itemId + '/history')
    setHistory(res.data)
    const found = items.find(i => i.id === itemId)
    setSelectedItem(found || null)
    setAiAnalysis(null)
  }

  const fetchAIAnalysis = async (itemId) => {
    setLoading(true)
    try {
      const res = await axios.get(API_URL + '/api/ai/analyze/' + itemId)
      setAiAnalysis(res.data)
    } catch (e) { console.error('AI error:', e) }
    setLoading(false)
  }

  const seedMockData = async (itemId) => {
    await axios.post(API_URL + '/api/ai/seed/' + itemId)
    fetchHistory(itemId)
    setTimeout(() => fetchAIAnalysis(itemId), 500)
  }

  const addItem = async () => {
    if (!newUrl || !targetPrice) return
    try {
      await axios.post(API_URL + '/api/items/?user_id=' + userId, {
        name: newName || 'Product',
        url: newUrl,
        store: 'generic',
        target_price: parseFloat(targetPrice),
      })
      setNewUrl('')
      setNewName('')
      setTargetPrice('')
      fetchItems()
    } catch (e) { console.error('Add error:', e) }
  }

  const deleteItem = async (id) => {
    try {
      await axios.delete(API_URL + '/api/items/' + id)
      if (selectedItem && selectedItem.id === id) {
        setSelectedItem(null)
        setHistory([])
        setAiAnalysis(null)
      }
      fetchItems()
    } catch (e) { console.error('Delete error:', e) }
  }

  const startEditTarget = (item) => {
    setEditingId(item.id)
    setEditTarget(item.target_price ? String(item.target_price) : '')
  }

  const saveTargetPrice = async (id) => {
    if (editTarget && !isNaN(parseFloat(editTarget))) {
      try {
        await axios.patch(API_URL + `/api/items/${id}/target`, null, {
          params: { target_price: parseFloat(editTarget) }
        })
        fetchItems()
      } catch (e) { console.error('Update target error:', e) }
    }
    setEditingId(null)
    setEditTarget('')
  }

  const currencySymbol = history.length > 0 ? (history[0].currency || '$') : '$'
  const avgPrice = items.length > 0
    ? (items.reduce((sum, item) => sum + (item.current_price || 0), 0) / items.length).toFixed(2)
    : '0.00'
  const bestDeal = items.length > 0 ? items.reduce((best, item) => {
    if (!best || item.current_price < best.current_price) return item
    return best
  }, null) : null

  const chartData = {
    labels: history.map((h) => new Date(h.checked_at).toLocaleDateString()),
    datasets: [{
      label: 'Price (' + currencySymbol + ')',
      data: history.map((h) => h.price),
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.3,
      fill: true,
    }],
  }

  if (!loggedIn) {
    return (
      <div style={{ padding: '20px', maxWidth: '400px', margin: '60px auto', fontFamily: 'system-ui', textAlign: 'center' }}>
        <h1>📦 PriceTracker</h1>
        <p style={{ color: '#666' }}>Enter your Telegram User ID to access your dashboard</p>
        <div style={{ background: '#f5f5f5', padding: '24px', borderRadius: '12px', marginTop: '20px' }}>
          <input type="number" placeholder="Your Telegram User ID" value={userId}
            onChange={(e) => setUserId(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
            style={{ padding: '12px', width: '100%', marginBottom: '12px', fontSize: '16px', boxSizing: 'border-box' }} />
          <button onClick={handleLogin} style={{ padding: '12px 24px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', width: '100%', fontSize: '16px' }}>Sign In</button>
          <p style={{ fontSize: '12px', color: '#999', marginTop: '12px' }}>Find your ID: send /start to @userinfobot on Telegram</p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto', fontFamily: 'system-ui' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>📦 PriceTracker</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ color: '#666', fontSize: '14px' }}>ID: {userId}</span>
          <button onClick={handleLogout} style={{ padding: '6px 12px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Sign Out</button>
        </div>
      </div>
      <p style={{ color: '#666' }}>Track product prices and get AI-powered recommendations</p>

      {items.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '20px' }}>
          <div style={{ background: '#10b981', color: 'white', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold' }}>{items.length}</div>
            <div style={{ fontSize: '13px', opacity: 0.9 }}>Items Tracked</div>
          </div>
          <div style={{ background: '#3b82f6', color: 'white', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold' }}>{avgPrice}</div>
            <div style={{ fontSize: '13px', opacity: 0.9 }}>Average Price</div>
          </div>
          {bestDeal && (
            <div style={{ background: '#f59e0b', color: 'white', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '28px', fontWeight: 'bold' }}>{currencySymbol}{bestDeal.current_price}</div>
              <div style={{ fontSize: '13px', opacity: 0.9 }}>Best Deal</div>
            </div>
          )}
          <div style={{ background: '#8b5cf6', color: 'white', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold' }}>🤖</div>
            <div style={{ fontSize: '13px', opacity: 0.9 }}>AI Powered</div>
          </div>
        </div>
      )}

      <div style={{ background: '#f5f5f5', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
        <h3>Add New Item</h3>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <input type="text" placeholder="Product name" value={newName} onChange={(e) => setNewName(e.target.value)} style={{ padding: '8px', flex: 1, minWidth: '150px' }} />
          <input type="text" placeholder="Product URL" value={newUrl} onChange={(e) => setNewUrl(e.target.value)} style={{ padding: '8px', flex: 2, minWidth: '200px' }} />
          <input type="number" placeholder="Target price *" value={targetPrice} onChange={(e) => setTargetPrice(e.target.value)} style={{ padding: '8px', width: '160px' }} />
          <button onClick={addItem} style={{ padding: '8px 16px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Add Item</button>
        </div>
      </div>

      <h2>Your Items ({items.length})</h2>
      {items.length === 0 ? (
        <p style={{ color: '#666' }}>No tracked items yet.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {items.map((item) => (
            <li key={item.id} style={{ padding: '12px', marginBottom: '8px', background: '#f0f9ff', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
              <div>
                <strong>{item.name}</strong><br />
                <span style={{ color: '#666' }}>{item.currency || '$'}{item.current_price} | {item.store}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                {editingId === item.id ? (
                  <>
                    <input type="number" value={editTarget} onChange={(e) => setEditTarget(e.target.value)}
                      style={{ padding: '4px', width: '80px', fontSize: '13px' }}
                      onKeyDown={(e) => e.key === 'Enter' && saveTargetPrice(item.id)} />
                    <button onClick={() => saveTargetPrice(item.id)} style={{ padding: '4px 8px', fontSize: '12px', background: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Save</button>
                    <button onClick={() => setEditingId(null)} style={{ padding: '4px 8px', fontSize: '12px', background: '#999', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>✕</button>
                  </>
                ) : (
                  <span style={{ color: '#f59e0b', fontSize: '0.85em', cursor: 'pointer', textDecoration: 'underline' }}
                    onClick={() => startEditTarget(item)}>
                    🎯 {item.target_price ? `<${item.currency || '$'}${item.target_price}` : 'Set target'}
                  </span>
                )}
                <button onClick={() => fetchHistory(item.id)} style={{ padding: '6px 12px', background: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '13px' }}>View Chart</button>
                <button onClick={() => deleteItem(item.id)} style={{ padding: '6px 12px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '13px' }}>Delete</button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {selectedItem && (
        <div style={{ marginTop: '30px' }}>
          <h2>Price History: {selectedItem.name}</h2>
          {history.length > 0 ? <Line data={chartData} /> : <p>No price history yet.</p>}
          <div style={{ marginTop: '16px', display: 'flex', gap: '10px' }}>
            <button onClick={() => seedMockData(selectedItem.id)} style={{ padding: '10px 20px', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>🎲 Generate Demo Data</button>
            <button onClick={() => fetchAIAnalysis(selectedItem.id)} disabled={loading} style={{ padding: '10px 20px', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: '6px', cursor: loading ? 'not-allowed' : 'pointer' }}>🤖 AI: Buy or Wait?</button>
          </div>
          {aiAnalysis && (
            <div style={{ marginTop: '16px', padding: '16px', background: aiAnalysis.recommendation === 'BUY NOW' ? '#dcfce7' : '#fef3c7', borderRadius: '8px', border: '2px solid ' + (aiAnalysis.recommendation === 'BUY NOW' ? '#22c55e' : '#f59e0b') }}>
              <h3 style={{ margin: '0 0 8px 0' }}>{aiAnalysis.recommendation === 'BUY NOW' ? '✅ BUY NOW' : '⏳ WAIT'}</h3>
              <p>{aiAnalysis.reason}</p>
              <div style={{ display: 'flex', gap: '16px', fontSize: '14px', color: '#666' }}>
                <span>Avg: {currencySymbol}{aiAnalysis.avg_price}</span>
                <span>Min: {currencySymbol}{aiAnalysis.min_price}</span>
                <span>Max: {currencySymbol}{aiAnalysis.max_price}</span>
                <span>Trend: {aiAnalysis.trend}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
