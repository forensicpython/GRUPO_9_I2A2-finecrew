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
  Link,
  Collapse,
  IconButton,
  Switch,
  FormControlLabel,
  Chip,
} from '@mui/material';
import {
  Help as HelpIcon,
  CheckCircle as CheckIcon,
  PlayArrow as TestIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { GroqConfig } from '../types';

interface ConfigurationPageProps {
  onConfigComplete: (config: GroqConfig) => void;
  initialConfig?: GroqConfig | null;
}

const ConfigurationPage: React.FC<ConfigurationPageProps> = ({
  onConfigComplete,
  initialConfig,
}) => {
  // Usar a chave do .env como padrão
  const defaultApiKey = '';
  const defaultModel = 'llama-3.3-70b-versatile';

  const [apiKey, setApiKey] = useState(initialConfig?.apiKey || defaultApiKey);
  const [model, setModel] = useState(initialConfig?.model || defaultModel);
  const [error, setError] = useState<string>('');
  const [testing, setTesting] = useState<boolean>(false);
  const [testResult, setTestResult] = useState<string>('');
  const [showHelp, setShowHelp] = useState<boolean>(false);
  const [useDefaultConfig, setUseDefaultConfig] = useState<boolean>(true);
  const [defaultKeyTested, setDefaultKeyTested] = useState<boolean>(false);
  const [defaultKeyWorking, setDefaultKeyWorking] = useState<boolean>(false);

  const testDefaultGroqConnection = async () => {
    setTesting(true);
    setError('');
    setTestResult('');

    try {
      console.log('🧪 Testando chave padrão do Groq...');

      const response = await fetch('/api/test-groq', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      console.log('📡 Resposta do teste:', data);

      if (data.groq_working) {
        setTestResult('success');
        setDefaultKeyTested(true);
        setDefaultKeyWorking(true);
        setError('');
      } else {
        setTestResult('warning');
        setDefaultKeyTested(true);
        setDefaultKeyWorking(false);
        setError(data.message || 'Chave padrão não está funcionando');
      }
    } catch (err) {
      console.error('❌ Erro no teste:', err);
      setTestResult('error');
      setDefaultKeyTested(true);
      setDefaultKeyWorking(false);
      setError('Erro ao testar conexão com o Groq');
    } finally {
      setTesting(false);
    }
  };

  const testConnection = async () => {
    if (!apiKey.trim()) {
      setError('Chave da API é obrigatória para teste');
      return;
    }

    setTesting(true);
    setError('');
    setTestResult('');

    try {
      console.log('🔄 Testando conexão com Groq...', { model });

      const response = await fetch('http://localhost:5000/api/test-groq-config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          apiKey: apiKey.trim(),
          model,
        }),
      });

      console.log('📡 Resposta recebida:', response.status, response.statusText);

      // Verificar se a resposta é JSON válido
      let data;
      try {
        data = await response.json();
      } catch (jsonError) {
        console.error('❌ Erro ao parsear JSON:', jsonError);
        throw new Error('Resposta inválida do servidor');
      }

      console.log('📋 Dados da resposta:', data);

      if (response.ok) {
        setTestResult(`✅ Conexão com Groq estabelecida com sucesso! Modelo: ${data.model_used || model}`);
        setError(''); // Limpar erro anterior
      } else {
        // Extrair mensagem de erro mais amigável
        let errorMessage = data.error || 'Erro ao conectar com Groq';

        // Melhorar mensagens de erro comuns
        if (errorMessage.includes('Invalid API Key')) {
          errorMessage = 'Chave da API inválida. Verifique se a chave está correta.';
        } else if (errorMessage.includes('401')) {
          errorMessage = 'Chave da API inválida ou expirada.';
        } else if (errorMessage.includes('403')) {
          errorMessage = 'Acesso negado. Verifique as permissões da sua chave API.';
        } else if (errorMessage.includes('429')) {
          errorMessage = 'Limite de requisições atingido. Tente novamente em alguns segundos.';
        }

        setError(errorMessage);
        setTestResult(''); // Limpar resultado anterior
      }
    } catch (err) {
      console.error('❌ Erro na requisição:', err);

      let errorMessage = 'Erro de rede ao testar conexão';

      if (err instanceof TypeError && err.message.includes('fetch')) {
        errorMessage = 'Erro de conexão: Verifique se o backend está rodando na porta 5000';
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }

      setError(errorMessage);
      setTestResult(''); // Limpar resultado anterior
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

  const handleUseDefaultToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
    const checked = event.target.checked;
    setUseDefaultConfig(checked);

    if (checked) {
      setApiKey(defaultApiKey);
      setModel(defaultModel);
      setError('');
      setTestResult('✅ Usando configuração padrão pré-testada!');
    } else {
      setApiKey('');
      setModel(defaultModel);
      setTestResult('');
    }
  };

  return (
    <Box>
      <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
        Configure as credenciais da API Groq para processar os arquivos VR/VA.
      </Typography>

      {/* Opção de configuração padrão */}
      <Card sx={{ mb: 3, bgcolor: useDefaultConfig ? 'success.50' : 'background.paper' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckIcon color="success" />
              <Typography variant="h6">Configuração Padrão</Typography>
              <Chip
                label="Recomendado"
                color="success"
                size="small"
                variant={useDefaultConfig ? "filled" : "outlined"}
              />
            </Box>
            <FormControlLabel
              control={
                <Switch
                  checked={useDefaultConfig}
                  onChange={handleUseDefaultToggle}
                  color="success"
                />
              }
              label="Usar configuração padrão"
            />
          </Box>

          {useDefaultConfig && (
            <>
              <Alert severity="success" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  <strong>Configuração ativa:</strong>
                </Typography>
                <Typography variant="body2">
                  • Chave API: {defaultApiKey.substring(0, 10)}...
                </Typography>
                <Typography variant="body2">
                  • Modelo: {defaultModel}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                  💡 Esta configuração foi pré-testada e está pronta para uso!
                </Typography>
              </Alert>

              {/* Botão para testar a chave padrão */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 2 }}>
                <Button
                  variant="outlined"
                  color="primary"
                  startIcon={testing ? <CircularProgress size={16} /> : <TestIcon />}
                  onClick={testDefaultGroqConnection}
                  disabled={testing}
                  size="small"
                >
                  {testing ? 'Testando...' : 'Testar Conexão Groq'}
                </Button>

                {defaultKeyTested && (
                  <Chip
                    icon={
                      defaultKeyWorking ? (
                        <CheckIcon />
                      ) : testResult === 'warning' ? (
                        <WarningIcon />
                      ) : (
                        <ErrorIcon />
                      )
                    }
                    label={
                      defaultKeyWorking
                        ? 'Chave funcionando!'
                        : testResult === 'warning'
                        ? 'Resposta inesperada'
                        : 'Erro na conexão'
                    }
                    color={
                      defaultKeyWorking
                        ? 'success'
                        : testResult === 'warning'
                        ? 'warning'
                        : 'error'
                    }
                    size="small"
                  />
                )}
              </Box>
            </>
          )}
        </CardContent>
      </Card>

      <Card sx={{ opacity: useDefaultConfig ? 0.6 : 1 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Configuração Personalizada
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {useDefaultConfig ?
              'Desative a configuração padrão acima para customizar as credenciais.' :
              'Configure suas próprias credenciais da API Groq.'
            }
          </Typography>

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

            <Box>
              <TextField
                label="Chave da API Groq"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                type="password"
                fullWidth
                required
                disabled={useDefaultConfig}
                placeholder="gsk_..."
                helperText={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <span>Obtenha sua chave em </span>
                    <Link href="https://console.groq.com/keys" target="_blank" rel="noopener">
                      https://console.groq.com/keys
                    </Link>
                    <IconButton size="small" onClick={() => setShowHelp(!showHelp)}>
                      <HelpIcon fontSize="small" />
                    </IconButton>
                  </Box>
                }
              />

              <Collapse in={showHelp}>
                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    <strong>Como obter sua chave da API Groq:</strong>
                  </Typography>
                  <Box component="ol" sx={{ pl: 2, mb: 0 }}>
                    <Typography component="li" variant="body2">
                      Acesse <Link href="https://console.groq.com" target="_blank">console.groq.com</Link>
                    </Typography>
                    <Typography component="li" variant="body2">
                      Faça login ou crie uma conta gratuita
                    </Typography>
                    <Typography component="li" variant="body2">
                      Vá para a seção "API Keys"
                    </Typography>
                    <Typography component="li" variant="body2">
                      Clique em "Create API Key"
                    </Typography>
                    <Typography component="li" variant="body2">
                      Copie a chave que começa com "gsk_" e cole aqui
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                    💡 A API Groq oferece uso gratuito com limite diário generoso!
                  </Typography>
                </Alert>
              </Collapse>
            </Box>

            <FormControl fullWidth>
              <InputLabel>Modelo</InputLabel>
              <Select
                value={model}
                label="Modelo"
                disabled={useDefaultConfig}
                onChange={(e) => setModel(e.target.value)}
              >
                <MenuItem value="llama-3.3-70b-versatile">Llama 3.3 70B Versatile (Recomendado)</MenuItem>
                <MenuItem value="deepseek-r1-distill-llama-70b">DeepSeek R1 Distill Llama 70B</MenuItem>
                <MenuItem value="llama3-groq-70b-8192-tool-use-preview">Llama 3 Groq 70B (Tool Use)</MenuItem>
                <MenuItem value="llama3-groq-8b-8192-tool-use-preview">Llama 3 Groq 8B (Rápido)</MenuItem>
                <MenuItem value="mixtral-8x7b-32768">Mixtral 8x7B</MenuItem>
                <MenuItem value="gemma-7b-it">Gemma 7B</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button
                variant="outlined"
                onClick={testConnection}
                disabled={testing || !apiKey.trim() || useDefaultConfig}
                startIcon={testing ? <CircularProgress size={16} /> : null}
                sx={{ flex: 1 }}
              >
                {useDefaultConfig ? 'Configuração Testada' : testing ? 'Testando...' : 'Testar Conexão'}
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