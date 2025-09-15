import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Stop as StopIcon,
  CheckCircle as SuccessIcon,
} from '@mui/icons-material';
import { GroqConfig, ProcessingResults } from '../types';

interface ProcessingPageProps {
  files: File[];
  groqConfig: GroqConfig | null;
  onComplete: (results: ProcessingResults) => void;
  processing: boolean;
  setProcessing: (processing: boolean) => void;
}

const ProcessingPage: React.FC<ProcessingPageProps> = ({
  files,
  groqConfig,
  onComplete,
  processing,
  setProcessing,
}) => {
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const startProcessing = async () => {
    if (!groqConfig) {
      setError('Configuração da API não encontrada');
      return;
    }

    setProcessing(true);
    setError('');
    setProgress(0);
    setLogs([]);
    
    addLog('Iniciando processamento...');

    try {
      addLog(`Processando ${files.length} arquivo(s) previamente carregados`);
      
      // Criar AbortController para timeout customizado
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 minutos

      const response = await fetch('/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Groq-Config': JSON.stringify({
            apiKey: groqConfig.apiKey,
            model: groqConfig.model
          })
        },
        body: JSON.stringify({}),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorMessage = `Erro no servidor: ${response.status}`;
        try {
          const errorText = await response.text();
          if (errorText) {
            errorMessage += ` - ${errorText}`;
          }
        } catch (e) {
          // Não conseguiu ler o texto do erro
        }
        throw new Error(errorMessage);
      }

      // Backend retorna JSON simples, não streaming
      const result = await response.json();
      
      if (result.status === 'success') {
        addLog('Processamento concluído com sucesso!');
        setProgress(100);
        onComplete(result);
      } else {
        throw new Error(result.error || 'Erro no processamento');
      }
      
    } catch (err) {
      let errorMessage = 'Erro desconhecido';
      
      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          errorMessage = 'Processamento interrompido por timeout (10 minutos). Tente novamente.';
        } else if (err.message.includes('Failed to fetch')) {
          errorMessage = 'Erro de conexão com o servidor. Verifique se o backend está funcionando.';
        } else if (err.message.includes('JSON')) {
          errorMessage = 'Erro de formato de resposta do servidor. Verifique os logs do backend.';
        } else {
          errorMessage = err.message;
        }
      }
      
      setError(errorMessage);
      addLog(`Erro: ${errorMessage}`);
    } finally {
      setProcessing(false);
      setProgress(0);
      setCurrentFile('');
    }
  };

  const stopProcessing = () => {
    setProcessing(false);
    addLog('Processamento interrompido pelo usuário');
  };

  return (
    <Box>
      <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
        Processe os arquivos carregados usando IA para análise de dados VR/VA.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Informações dos Arquivos */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Arquivos para Processamento
          </Typography>
          <List dense>
            {files.map((file, index) => (
              <ListItem key={index}>
                <ListItemText
                  primary={file.name}
                  secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                />
                <Chip
                  icon={processing && currentFile === file.name ? <CircularProgress size={16} /> : <SuccessIcon />}
                  label={processing && currentFile === file.name ? 'Processando' : 'Pronto'}
                  color={processing && currentFile === file.name ? 'primary' : 'success'}
                  size="small"
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Controles de Processamento */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Processamento
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              {!processing ? (
                <Button
                  variant="contained"
                  startIcon={<StartIcon />}
                  onClick={startProcessing}
                  disabled={files.length === 0 || !groqConfig}
                >
                  Iniciar Processamento
                </Button>
              ) : (
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<StopIcon />}
                  onClick={stopProcessing}
                >
                  Parar
                </Button>
              )}
            </Box>
          </Box>

          {processing && (
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">
                  {currentFile || 'Processando...'}
                </Typography>
                <Typography variant="body2">
                  {Math.round(progress)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  bgcolor: 'rgba(99, 102, 241, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: 'primary.main',
                  },
                }}
              />
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Logs */}
      {logs.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Logs de Processamento
            </Typography>
            <Box
              sx={{
                maxHeight: 200,
                overflow: 'auto',
                bgcolor: 'background.default',
                p: 2,
                borderRadius: 1,
                fontFamily: 'monospace',
                fontSize: '0.875rem',
              }}
            >
              {logs.map((log, index) => (
                <Typography
                  key={index}
                  variant="body2"
                  sx={{ color: 'text.primary', mb: 0.5 }}
                >
                  {log}
                </Typography>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ProcessingPage;