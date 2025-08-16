import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
  IconButton,
  InputAdornment,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Settings,
  Visibility,
  VisibilityOff,
  CheckCircle,
  Error,
  Info,
  VpnKey,
  Computer,
  Speed,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';

interface ConfigurationStepProps {
  onConfigurationComplete: (config: GroqConfig) => void;
  initialConfig?: GroqConfig;
}

export interface GroqConfig {
  apiKey: string;
  model: string;
  requestDelay: number;
  requestTimeout: number;
  maxRetries: number;
}

const availableModels = [
  {
    id: 'meta-llama/llama-4-maverick-17b-128e-instruct',
    name: 'Llama 4 Maverick 17B',
    description: 'Modelo de última geração com 128e de contexto',
    recommended: true
  },
  {
    id: 'deepseek-r1-distill-llama-70b', 
    name: 'DeepSeek R1 Distill 70B',
    description: 'Modelo otimizado com alta capacidade analítica'
  },
  {
    id: 'qwen/qwen3-32b',
    name: 'Qwen 3 32B',
    description: 'Excelente para processamento multilíngue'
  },
  {
    id: 'llama-3.3-70b-versatile',
    name: 'Llama 3.3 70B Versatile',
    description: 'Versátil e poderoso para tarefas complexas'
  }
];

const ConfigurationStep: React.FC<ConfigurationStepProps> = ({ 
  onConfigurationComplete, 
  initialConfig 
}) => {
  const [config, setConfig] = useState<GroqConfig>({
    apiKey: initialConfig?.apiKey || '',
    model: initialConfig?.model || 'meta-llama/llama-4-maverick-17b-128e-instruct',
    requestDelay: initialConfig?.requestDelay || 2,
    requestTimeout: initialConfig?.requestTimeout || 60,
    maxRetries: initialConfig?.maxRetries || 3
  });

  const [showApiKey, setShowApiKey] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<'success' | 'error' | null>(null);
  const [testMessage, setTestMessage] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    // Carregar configuração salva do localStorage
    const savedConfig = localStorage.getItem('finacrew_groq_config');
    if (savedConfig) {
      try {
        const parsed = JSON.parse(savedConfig);
        setConfig(prev => ({ ...prev, ...parsed }));
      } catch (error) {
        console.error('Erro ao carregar configuração salva:', error);
      }
    }
  }, []);

  const handleConfigChange = (field: keyof GroqConfig, value: string | number) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
    setTestResult(null); // Reset test result when config changes
  };

  const saveConfiguration = () => {
    // Salvar no localStorage (sem a API key por segurança)
    const configToSave = {
      model: config.model,
      requestDelay: config.requestDelay,
      requestTimeout: config.requestTimeout,
      maxRetries: config.maxRetries
    };
    localStorage.setItem('finacrew_groq_config', JSON.stringify(configToSave));
    
    onConfigurationComplete(config);
  };

  const testApiConnection = async () => {
    if (!config.apiKey.trim()) {
      setTestResult('error');
      setTestMessage('Por favor, insira uma chave de API válida');
      return;
    }

    setTesting(true);
    setTestResult(null);
    setTestMessage('');

    try {
      const response = await fetch('/api/test-groq-config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
      });

      const result = await response.json();

      if (response.ok && result.status === 'success') {
        setTestResult('success');
        setTestMessage(`Conexão estabelecida com sucesso! Modelo: ${result.model_used}`);
      } else {
        setTestResult('error');
        setTestMessage(result.error || 'Falha na conexão com a API Groq');
      }
    } catch (error) {
      setTestResult('error');
      setTestMessage('Erro ao testar conexão. Verifique sua rede e tente novamente.');
    } finally {
      setTesting(false);
    }
  };

  const isConfigValid = config.apiKey.trim().length > 0 && config.model.trim().length > 0;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Header */}
      <Paper elevation={2} sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Settings sx={{ mr: 2, fontSize: 32, color: 'primary.main' }} />
          <Box>
            <Typography variant="h5" component="h2" gutterBottom>
              Configuração da API Groq
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Configure sua chave de API e modelo para processar os dados do FinaCrew
            </Typography>
          </Box>
        </Box>

        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="body2">
            <strong>Como obter sua chave Groq:</strong><br/>
            1. Acesse <a href="https://console.groq.com" target="_blank" rel="noopener noreferrer">console.groq.com</a><br/>
            2. Faça login ou crie uma conta gratuita<br/>
            3. Vá em "API Keys" e gere uma nova chave<br/>
            4. Cole a chave no campo abaixo
          </Typography>
        </Alert>
      </Paper>

      <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
        {/* Configuração Principal */}
        <Box sx={{ flex: '2 1 500px' }}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Configuração Principal
              </Typography>

              {/* API Key */}
              <TextField
                fullWidth
                label="Chave da API Groq"
                placeholder="gsk_..."
                value={config.apiKey}
                onChange={(e) => handleConfigChange('apiKey', e.target.value)}
                type={showApiKey ? 'text' : 'password'}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <VpnKey color="primary" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowApiKey(!showApiKey)}
                        edge="end"
                      >
                        {showApiKey ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                helperText="Sua chave será usada apenas para esta sessão e não será armazenada"
              />

              {/* Modelo */}
              <FormControl fullWidth margin="normal" required>
                <InputLabel>Modelo de IA</InputLabel>
                <Select
                  value={config.model}
                  label="Modelo de IA"
                  onChange={(e) => handleConfigChange('model', e.target.value)}
                  startAdornment={
                    <InputAdornment position="start">
                      <Computer color="primary" />
                    </InputAdornment>
                  }
                >
                  {availableModels.map((model) => (
                    <MenuItem key={model.id} value={model.id}>
                      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="body1">
                            {model.name}
                            {model.recommended && (
                              <Chip 
                                label="Recomendado" 
                                size="small" 
                                color="primary" 
                                sx={{ ml: 1 }} 
                              />
                            )}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {model.description}
                          </Typography>
                        </Box>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Test Connection */}
              <Box sx={{ mt: 3, mb: 2 }}>
                <Button
                  variant="outlined"
                  onClick={testApiConnection}
                  disabled={!config.apiKey.trim() || testing}
                  startIcon={testing ? <Speed className="rotate" /> : <CheckCircle />}
                  fullWidth
                >
                  {testing ? 'Testando Conexão...' : 'Testar Conexão'}
                </Button>

                {testResult && (
                  <Alert 
                    severity={testResult} 
                    sx={{ mt: 2 }}
                    icon={testResult === 'success' ? <CheckCircle /> : <Error />}
                  >
                    {testMessage}
                  </Alert>
                )}
              </Box>

              {/* Advanced Settings */}
              <Box>
                <Button
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  startIcon={showAdvanced ? <ExpandLess /> : <ExpandMore />}
                  sx={{ mb: 1 }}
                >
                  Configurações Avançadas
                </Button>

                <Collapse in={showAdvanced}>
                  <Box sx={{ pl: 2, borderLeft: '2px solid', borderColor: 'divider' }}>
                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                      <Box sx={{ flex: '1 1 150px' }}>
                        <TextField
                          fullWidth
                          label="Delay entre Requests (s)"
                          type="number"
                          value={config.requestDelay}
                          onChange={(e) => handleConfigChange('requestDelay', Number(e.target.value))}
                          inputProps={{ min: 1, max: 10 }}
                          size="small"
                          helperText="Intervalo entre chamadas"
                        />
                      </Box>
                      <Box sx={{ flex: '1 1 150px' }}>
                        <TextField
                          fullWidth
                          label="Timeout (s)"
                          type="number"
                          value={config.requestTimeout}
                          onChange={(e) => handleConfigChange('requestTimeout', Number(e.target.value))}
                          inputProps={{ min: 30, max: 300 }}
                          size="small"
                          helperText="Tempo limite por request"
                        />
                      </Box>
                      <Box sx={{ flex: '1 1 150px' }}>
                        <TextField
                          fullWidth
                          label="Max Tentativas"
                          type="number"
                          value={config.maxRetries}
                          onChange={(e) => handleConfigChange('maxRetries', Number(e.target.value))}
                          inputProps={{ min: 1, max: 5 }}
                          size="small"
                          helperText="Tentativas em caso de erro"
                        />
                      </Box>
                    </Box>
                  </Box>
                </Collapse>
              </Box>

              {/* Action Button */}
              <Box sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={saveConfiguration}
                  disabled={!isConfigValid}
                  fullWidth
                  sx={{ py: 1.5 }}
                >
                  Salvar Configuração e Continuar
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Info Panel */}
        <Box sx={{ flex: '1 1 300px' }}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Informações dos Modelos
              </Typography>
              
              <List dense>
                {availableModels.map((model) => (
                  <ListItem key={model.id}>
                    <ListItemIcon>
                      {model.recommended ? (
                        <CheckCircle color="primary" />
                      ) : (
                        <Computer color="action" />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={model.name}
                      secondary={model.description}
                    />
                  </ListItem>
                ))}
              </List>

              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  <strong>Recomendação:</strong> Use o Llama 4 Maverick 17B para melhor equilíbrio entre performance e capacidade de contexto no processamento do FinaCrew.
                </Typography>
              </Alert>
            </CardContent>
          </Card>

          <Card elevation={2} sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Segurança
              </Typography>
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircle color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Chave não armazenada"
                    secondary="Usada apenas durante a sessão"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircle color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Conexão criptografada"
                    secondary="HTTPS para todas as comunicações"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircle color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Configuração local"
                    secondary="Preferências salvas no navegador"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default ConfigurationStep;