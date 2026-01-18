import { useState } from 'react'
import axios from 'axios'
import { 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Paper,
  Box,
  CircularProgress, 
  Grid,
} from '@mui/material'
import {
  BarChart, 
  Bar, 
  XAxis, 
  YAxis,
  CartesianGrid, 
  Tooltip,
  Legend, 
  ResponsiveContainer,
  LineChart, 
  Line
} from 'recharts'

// 定义接口
interface HistoryItem {
  date: string;
  additions: number;
  deletions: number;
  author: string;
}

// 定义接口返回的数据类型 (TypeScript 的优势)
interface AnalysisResult {
  project_id: number;
  health_score: number;
  commits_stored: number;
  history: HistoryItem[];
}

function App() {
  const [repoStr, setRepoStr] = useState("tiangolo/fastapi")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState("")

  // 处理数据，使其适合图表展示
  // 因为后端返回的是 commit 粒度，我们需要按天聚合一下吗？
  // MVP 阶段：直接按 Commit 展示即可，或者反转数组（因为 GitHub 返回的是最新的在前面）
  const getChartData = () => {
    if (!result) return []
    // 浅拷贝并反转，让旧的在左边，新的在右边，符合时间轴直觉
    const data = [...result.history].reverse().map(item => ({
      ...item,
      // 简单格式化日期，只显示月-日
      shortDate: new Date(item.date).toLocaleDateString()
    }))
    return data
  }

  const handleAnalyze = async () => {
    setLoading(true)
    setError("")
    setResult(null)
    
    try {
      // 解析 owner/repo
      const [owner, repo] = repoStr.split('/')
      if (!owner || !repo) {
        throw new Error("Invalid format. Use 'owner/repo'")
      }

      // 发送请求给后端
      const response = await axios.get(`http://127.0.0.1:8000/api/analyze/${owner}/${repo}`)
      setResult(response.data)
      
    } catch (err: any) {
      console.error(err)
      setError(err.response?.data?.detail || err.message || "An error occurred")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 8 }}>
      <Typography variant="h3" gutterBottom align="center">
        GitHub Health Dashboard
      </Typography>
      
      {/* 输入区域 */}
      <Paper sx={{ p: 4, display: 'flex', gap: 2 }}>
        <TextField 
          fullWidth 
          label="GitHub Repository (e.g. facebook/react)" 
          value={repoStr}
          onChange={(e) => setRepoStr(e.target.value)}
        />
        <Button 
          variant="contained" 
          size="large" 
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Analyze"}
        </Button>
      </Paper>

      {/* 结果展示区域 */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        {loading && <CircularProgress />}
        
        {error && (
          <Typography color="error">
            {error}
          </Typography>
        )}

        {result && (
          <Box>
            {/* 分数大卡片 */}
            <Paper sx={{ p: 4, bgcolor: '#f5f5f5' }}>
              <Typography variant="h2" color="primary">
                {result.health_score}
              </Typography>
              <Typography variant="subtitle1" color="textSecondary">
                Project Health Score
              </Typography>
            </Paper>

            {/* 图表区域 */}
            <Grid container spacing={3}>
              {/* 图表 A: 代码变动趋势 */}
              <Grid size={{ xs: 12, md: 6 }}>
                <Paper sx={{ p: 2, height: 400 }}>
                  <Typography variant="h6" gutterBottom>Code Churn (Add vs Del)</Typography>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getChartData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="shortDate" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="additions" fill="#82ca9d" name="Added" />
                      <Bar dataKey="deletions" fill="#ff8042" name="Deleted" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>

              {/* 图表 B: 提交时间轴 (Line Chart) */}
              <Grid size={{ xs: 12, md: 6 }}>
                 <Paper sx={{ p: 2, height: 400 }}>
                  <Typography variant="h6" gutterBottom>Commit Impact</Typography>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={getChartData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="shortDate" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="additions" stroke="#8884d8" dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}
      </Box>
    </Container>
  )
}

export default App