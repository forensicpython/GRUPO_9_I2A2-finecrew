import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  CircularProgress,
} from '@mui/material';
import { GroqConfig } from '../types';

interface ConfigurationPageProps {
  onConfigComplete: (config: GroqConfig) => void;
  initialConfig?: GroqConfig | null;
}

const ConfigurationPage: React.FC<ConfigurationPageProps> = ({
  onConfigComplete,
  initialConfig,
}) => {
  const [apiKey, setApiKey] = useState(initialConfig?.apiKey || '');
  const [model, setModel] = useState(initialConfig?.model || 'deepseek-r1-distill-llama-70b');
  const [error, setError] = useState<string>('');
  const [testing, setTesting] = useState<boolean>(false);
  const [testResult, setTestResult] = useState<string>('');

  const testConnection = async () => {
    if (!apiKey.trim()) {
      setError('Chave da API é obrigatória para teste');
      return;
    }

    setTesting(true);
    setError('');
    setTestResult('');

    try {
      const response = await fetch('/api/test-groq-config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          apiKey: apiKey.trim(),
          model,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setTestResult('✅ Conexão com Groq estabelecida com sucesso!');
      } else {
        setError(data.error || 'Erro ao conectar com Groq');
      }
    } catch (err) {
      setError('Erro de rede ao testar conexão');
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!apiKey.trim()) {
      setError('Chave da API é obrigatória');
      return;
    }

    if (!model) {
      setError('Modelo é obrigatório');
      return;
    }

    onConfigComplete({ apiKey: apiKey.trim(), model });
  };

  return (
    <Box>
      <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
        Configure as credenciais da API Groq para processar os arquivos VR/VA.
      </Typography>

      <Card>
        <CardContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {testResult && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {testResult}
              </Alert>
            )}

            <TextField
              label="Chave da API Groq"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              type="password"
              fullWidth
              required
              placeholder="gsk_..."
              helperText="Obtenha sua chave em https://console.groq.com/keys"
            />

            <FormControl fullWidth>
              <InputLabel>Modelo</InputLabel>
              <Select
                value={model}
                label="Modelo"
                onChange={(e) => setModel(e.target.value)}
              >
                <MenuItem value="deepseek-r1-distill-llama-70b">DeepSeek R1 Distill Llama 70B</MenuItem>
                <MenuItem value="qwen/qwen3-32b">Qwen 3 32B</MenuItem>
                <MenuItem value="llama-3.3-70b-versatile">Llama 3.3 70B Versatile</MenuItem>
                <MenuItem value="openai/gpt-oss-120b">OpenAI GPT OSS 120B</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button
                variant="outlined"
                onClick={testConnection}
                disabled={testing || !apiKey.trim()}
                startIcon={testing ? <CircularProgress size={16} /> : null}
                sx={{ flex: 1 }}
              >
                {testing ? 'Testando...' : 'Testar Conexão'}
              </Button>

              <Button
                type="submit"
                variant="contained"
                size="large"
                sx={{ flex: 2 }}
              >
                Continuar
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ConfigurationPage;