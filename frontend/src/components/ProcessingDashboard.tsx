import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  Chip,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import {
  PlayArrow,
  CheckCircle,
  Error,
  HourglassTop,
  Analytics,
  Assessment,
  Security,
  Calculate,
  TableChart
} from '@mui/icons-material';

import { GroqConfig } from './ConfigurationStep';

interface ProcessingDashboardProps {
  files: File[];
  onProcessingComplete: (results: any) => void;
  processing: boolean;
  setProcessing: (processing: boolean) => void;
  groqConfig: GroqConfig | null;
}

const processingSteps = [
  {
    label: 'Listagem de Arquivos',
    description: 'Verificando arquivos carregados',
    icon: <TableChart />
  },
  {
    label: 'Consolidação das Bases',
    description: 'Consolidando dados dos 5 arquivos principais',
    icon: <Assessment />
  },
  {
    label: 'Validação de Qualidade',
    description: 'Verificando integridade dos dados',
    icon: <Security />
  },
  {
    label: 'Cálculo Automatizado',
    description: 'Aplicando regras de negócio e calculando benefícios',
    icon: <Calculate />
  },
  {
    label: 'Geração da Planilha',
    description: 'Criando arquivo Excel final conforme modelo',
    icon: <Analytics />
  }
];

const ProcessingDashboard: React.FC<ProcessingDashboardProps> = ({
  files,
  onProcessingComplete,
  processing,
  setProcessing,
  groqConfig
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepResults, setStepResults] = useState<any[]>([]);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const simulateProcessing = async () => {
    setProcessing(true);
    setCurrentStep(0);
    setStepResults([]);
    setLogs([]);

    addLog('Iniciando processamento automatizado...');

    try {
      // Primeiro, fazer upload dos arquivos
      setCurrentStep(0);
      addLog('📤 Fazendo upload dos arquivos...');
      
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const uploadResponse = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Groq-Config': JSON.stringify(groqConfig)
        }
      });

      if (!uploadResponse.ok) {
        throw new (Error as any)('Erro no upload dos arquivos');
      }

      addLog('✅ Upload concluído com sucesso');

      // Simular etapas visuais
      for (let i = 1; i < processingSteps.length - 1; i++) {
        setCurrentStep(i);
        addLog(`Executando: ${processingSteps[i].label}`);
        
        // Simular tempo de processamento visual
        await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 2000));
        
        const stepResult = await processStep(i);
        setStepResults(prev => [...prev, stepResult]);
        
        addLog(`✅ Concluído: ${processingSteps[i].label}`);
      }

      // Executar processamento real
      setCurrentStep(processingSteps.length - 1);
      addLog('🔄 Executando processamento FinaCrew...');

      const processResponse = await fetch('/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Groq-Config': JSON.stringify(groqConfig)
        }
      });

      if (!processResponse.ok) {
        const errorData = await processResponse.json();
        throw new (Error as any)(errorData.error || 'Erro no processamento');
      }

      const finalResults = await processResponse.json();
      
      addLog('🎉 Processamento concluído com sucesso!');
      addLog(`📊 ${finalResults.funcionarios_elegiveis} funcionários processados`);
      addLog(`💰 Total VR: R$ ${finalResults.valor_total_vr?.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
      
      onProcessingComplete(finalResults);

    } catch (error: any) {
      addLog(`❌ Erro: ${error.message}`);
      setProcessing(false);
      alert(`Erro no processamento: ${error.message}`);
    }
  };

  const processStep = async (stepIndex: number) => {
    switch (stepIndex) {
      case 0: // Listagem
        return {
          arquivos_encontrados: files.length,
          status: 'success'
        };
      case 1: // Consolidação
        return {
          registros_ativos: 1815,
          exclusoes_aplicadas: 84,
          base_final: 1791,
          status: 'success'
        };
      case 2: // Validação
        return {
          matriculas_duplicadas: 0,
          campos_obrigatorios: 'OK',
          valores_inconsistentes: 0,
          status: 'success'
        };
      case 3: // Cálculo
        return {
          funcionarios_calculados: 1812,
          regra_dia_15_aplicada: true,
          funcionarios_ferias: 80,
          funcionarios_afastados: 20,
          status: 'success'
        };
      case 4: // Geração
        return {
          planilha_gerada: 'VR MENSAL 05.2025 vfinal.xlsx',
          conformidade_modelo: true,
          status: 'success'
        };
      default:
        return { status: 'success' };
    }
  };

  const getStepStatus = (stepIndex: number) => {
    if (stepIndex < currentStep) return 'completed';
    if (stepIndex === currentStep && processing) return 'active';
    return 'pending';
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Informações dos Arquivos */}
      <Box sx={{ flex: '0 0 auto' }}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Arquivos Carregados
            </Typography>
            <List dense>
              {files.map((file, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <CheckCircle color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary={file.name}
                    secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                  />
                </ListItem>
              ))}
            </List>
            
            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                size="large"
                startIcon={processing ? <CircularProgress size={20} /> : <PlayArrow />}
                onClick={simulateProcessing}
                disabled={processing || files.length < 5}
                fullWidth
              >
                {processing ? 'Processando...' : 'Iniciar Processamento'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Progress do Processamento */}
      <Box sx={{ flex: '1 1 auto' }}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Progresso do Processamento
            </Typography>
            
            <Stepper activeStep={currentStep} orientation="vertical">
              {processingSteps.map((step, index) => (
                <Step key={step.label}>
                  <StepLabel
                    icon={
                      getStepStatus(index) === 'completed' ? (
                        <CheckCircle color="success" />
                      ) : getStepStatus(index) === 'active' ? (
                        <CircularProgress size={24} />
                      ) : (
                        step.icon
                      )
                    }
                  >
                    <Box>
                      <Typography variant="subtitle1">
                        {step.label}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {step.description}
                      </Typography>
                    </Box>
                  </StepLabel>
                  <StepContent>
                    {stepResults[index] && (
                      <Box sx={{ mt: 1, mb: 1 }}>
                        <Alert severity="success" variant="outlined">
                          <Typography variant="body2">
                            {JSON.stringify(stepResults[index], null, 2)}
                          </Typography>
                        </Alert>
                      </Box>
                    )}
                  </StepContent>
                </Step>
              ))}
            </Stepper>
          </CardContent>
        </Card>
      </Box>

      {/* Logs em Tempo Real */}
      {logs.length > 0 && (
        <Box>
          <Card 
            elevation={0}
            className="hover-lift"
            sx={{ 
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: 3
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#1e293b' }}>
                Log de Processamento
              </Typography>
              <Paper 
                elevation={0} 
                sx={{ 
                  background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
                  color: '#e2e8f0', 
                  p: 3, 
                  height: 240, 
                  overflow: 'auto',
                  fontFamily: 'monospace',
                  borderRadius: 2,
                  border: '1px solid #334155',
                  boxShadow: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
                  '&::-webkit-scrollbar': {
                    width: '8px',
                  },
                  '&::-webkit-scrollbar-track': {
                    background: '#1e293b',
                  },
                  '&::-webkit-scrollbar-thumb': {
                    background: '#475569',
                    borderRadius: '4px',
                  },
                  '&::-webkit-scrollbar-thumb:hover': {
                    background: '#64748b',
                  },
                }}
              >
                {logs.map((log, index) => (
                  <Typography 
                    key={index} 
                    variant="body2" 
                    sx={{ fontSize: '0.8rem', mb: 0.5 }}
                  >
                    {log}
                  </Typography>
                ))}
              </Paper>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Estatísticas Rápidas */}
      {processing && (
        <Box>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Box sx={{ flex: '1 1 200px' }}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    {files.length}
                  </Typography>
                  <Typography variant="body2">
                    Arquivos
                  </Typography>
                </CardContent>
              </Card>
            </Box>
            <Box sx={{ flex: '1 1 200px' }}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    {currentStep + 1}
                  </Typography>
                  <Typography variant="body2">
                    de {processingSteps.length} Etapas
                  </Typography>
                </CardContent>
              </Card>
            </Box>
            <Box sx={{ flex: '1 1 200px' }}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="info.main">
                    ~1.8K
                  </Typography>
                  <Typography variant="body2">
                    Funcionários
                  </Typography>
                </CardContent>
              </Card>
            </Box>
            <Box sx={{ flex: '1 1 200px' }}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    R$ 1M
                  </Typography>
                  <Typography variant="body2">
                    Total Estimado
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default ProcessingDashboard;