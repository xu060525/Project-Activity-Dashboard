import { useState } from 'react'
import axios from 'axios'
import { 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Paper,
  Box,
  CircularProgress
} from '@mui/material'

// 定义接口返回的数据类型 (TypeScript 的优势)
interface AnalysisResult {
  project_id: number;
  health_score: number;
  commits_stored: number;
}

function App() {
  const [repoStr, setRepoStr] = useState("tiangolo/fastapi")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState("")

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
    <Container maxWidth="md" sx={{ mt: 4 }}>
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
          <Typography color="error" variant="h6">
            Error: {error}
          </Typography>
        )}

        {result && (
          <Paper sx={{ p: 4, bgcolor: '#f5f5f5' }}>
            <Typography variant="h2" color="primary">
              {result.health_score}
            </Typography>
            <Typography variant="subtitle1" color="textSecondary">
              Health Score
            </Typography>
            
            <Box sx={{ mt: 2 }}>
              <Typography>
                Processed {result.commits_stored} commits
              </Typography>
            </Box>
          </Paper>
        )}
      </Box>
    </Container>
  )
}

export default App