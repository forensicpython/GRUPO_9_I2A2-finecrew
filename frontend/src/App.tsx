import React, { useState, useCallback } from 'react';
import {
  Container,
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  Chip,
  Alert,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  AppBar,
  Toolbar,
  Fade,
  Slide,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Settings as ConfigIcon,
  PlayCircleOutline as ProcessIcon,
  CheckCircle as ResultsIcon,
  Info as InfoIcon,
  Assessment as ReportIcon,
  Business as CompanyIcon,
  People as PeopleIcon,
  AttachMoney as MoneyIcon,
  Schedule as TimeIcon,
} from '@mui/icons-material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { GroqConfig, ProcessingResults } from './types';
import UploadPage from './pages/UploadPage';
import ConfigurationPage from './pages/ConfigurationPage';
import ProcessingPage from './pages/ProcessingPage';
import ResultsPage from './pages/ResultsPage';

const steps = [
  { label: 'Upload de Arquivos', icon: UploadIcon },
  { label: 'Configuração', icon: ConfigIcon },
  { label: 'Processamento', icon: ProcessIcon },
  { label: 'Resultados', icon: ResultsIcon }
];

function App() {
  const [activeStep, setActiveStep] = useState(0);
  const [files, setFiles] = useState<any[]>([]);
  const [groqConfig, setGroqConfig] = useState<GroqConfig>({
    apiKey: '',
    model: 'llama-3.3-70b-versatile'
  });
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState<ProcessingResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  const theme = createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: '#4299e1', // Blue-400
        light: '#63b3ed', // Blue-300
        dark: '#2b6cb0', // Blue-600
        contrastText: '#ffffff',
      },
      secondary: {
        main: '#9ca3af', // Gray-400
        light: '#d1d5db', // Gray-300
        dark: '#6b7280', // Gray-500
      },
      background: {
        default: '#1a202c', // Dark blue-gray
        paper: 'rgba(45, 55, 72, 0.9)', // Glass morphism effect
      },
      text: {
        primary: '#f7fafc', // Almost white
        secondary: '#cbd5e0', // Light gray-blue
      },
      divider: 'rgba(66, 153, 225, 0.2)',
      error: {
        main: '#f56565',
      },
      warning: {
        main: '#ed8936',
      },
      info: {
        main: '#4299e1',
      },
      success: {
        main: '#48bb78',
      },
    },
    typography: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
      h4: {
        fontWeight: 700,
        letterSpacing: '-0.5px',
        background: 'linear-gradient(45deg, #4299e1 30%, #63b3ed 90%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
      },
      h6: {
        fontWeight: 600,
        color: '#f7fafc',
      },
      body1: {
        color: '#cbd5e0',
      },
      body2: {
        color: '#a0aec0',
      },
    },
    shape: {
      borderRadius: 16,
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            background: 'linear-gradient(145deg, rgba(45, 55, 72, 0.9), rgba(26, 32, 44, 0.9))',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(66, 153, 225, 0.2)',
            borderRadius: '16px',
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
            transition: 'all 0.3s ease',
            '&:hover': {
              border: '1px solid rgba(66, 153, 225, 0.4)',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.4), 0 0 30px rgba(66, 153, 225, 0.2)',
              transform: 'translateY(-4px)',
            },
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 600,
            borderRadius: '12px',
            padding: '12px 24px',
            boxShadow: '0 4px 15px rgba(66, 153, 225, 0.3)',
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: '0 8px 25px rgba(66, 153, 225, 0.4)',
            },
          },
          contained: {
            background: 'linear-gradient(45deg, #2b6cb0, #4299e1)',
            '&:hover': {
              background: 'linear-gradient(45deg, #2c5aa0, #3182ce)',
            },
          },
          outlined: {
            borderColor: 'rgba(66, 153, 225, 0.5)',
            color: '#4299e1',
            '&:hover': {
              borderColor: '#4299e1',
              backgroundColor: 'rgba(66, 153, 225, 0.1)',
            },
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            backdropFilter: 'blur(8px)',
            '&.MuiChip-colorPrimary': {
              background: 'rgba(66, 153, 225, 0.2)',
              border: '1px solid rgba(66, 153, 225, 0.3)',
              color: '#63b3ed',
            },
          },
        },
      },
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            borderRadius: '8px',
            height: '8px',
            backgroundColor: 'rgba(45, 55, 72, 0.8)',
          },
          bar: {
            background: 'linear-gradient(90deg, #2b6cb0, #4299e1, #63b3ed)',
            borderRadius: '8px',
            boxShadow: '0 2px 10px rgba(66, 153, 225, 0.3)',
          },
        },
      },
      MuiAlert: {
        styleOverrides: {
          root: {
            borderRadius: '12px',
            backdropFilter: 'blur(8px)',
          },
          standardError: {
            background: 'rgba(245, 101, 101, 0.1)',
            border: '1px solid rgba(245, 101, 101, 0.3)',
            color: '#feb2b2',
          },
          standardSuccess: {
            background: 'rgba(72, 187, 120, 0.1)',
            border: '1px solid rgba(72, 187, 120, 0.3)',
            color: '#9ae6b4',
          },
          standardInfo: {
            background: 'rgba(66, 153, 225, 0.1)',
            border: '1px solid rgba(66, 153, 225, 0.3)',
            color: '#90cdf4',
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            background: 'rgba(26, 32, 44, 0.95)',
            backdropFilter: 'blur(16px)',
            borderBottom: '1px solid rgba(66, 153, 225, 0.2)',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
          },
        },
      },
    },
  });

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
    setError(null);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
    setError(null);
  };

  const handleReset = () => {
    setActiveStep(0);
    setFiles([]);
    setResults(null);
    setError(null);
    setProcessing(false);
  };

  const handleFilesUpload = useCallback((uploadedFiles: any[]) => {
    setFiles(uploadedFiles);
    if (uploadedFiles.length > 0) {
      setTimeout(() => handleNext(), 500);
    }
  }, []);

  const handleConfigComplete = useCallback((config: GroqConfig) => {
    setGroqConfig(config);
    setTimeout(() => handleNext(), 500);
  }, []);

  const handleProcessComplete = useCallback((results: ProcessingResults) => {
    setResults(results);
    setProcessing(false);
    setTimeout(() => handleNext(), 1000);
  }, []);


  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return <UploadPage onFilesUpload={handleFilesUpload} files={files} />;
      case 1:
        return (
          <ConfigurationPage
            onConfigComplete={handleConfigComplete}
            initialConfig={groqConfig}
          />
        );
      case 2:
        return (
          <ProcessingPage
            files={files as File[]}
            groqConfig={groqConfig}
            onComplete={handleProcessComplete}
            processing={processing}
            setProcessing={setProcessing}
          />
        );
      case 3:
        return results ? <ResultsPage results={results} onReset={handleReset} /> : null;
      default:
        return null;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
        transition: 'all 0.3s ease',
      }}>
        <AppBar
          position="sticky"
          elevation={0}
          sx={{
            bgcolor: 'background.paper',
            borderBottom: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Toolbar>
            <CompanyIcon sx={{ mr: 2, color: 'primary.main' }} />
            <Typography
              variant="h6"
              component="div"
              sx={{
                flexGrow: 1,
                color: 'text.primary',
                fontWeight: 600,
              }}
            >
              FinaCrew
            </Typography>
            <Chip
              icon={<ReportIcon />}
              label="Sistema VR/VA"
              color="primary"
              variant="outlined"
              sx={{ mr: 2 }}
            />
          </Toolbar>
        </AppBar>

        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Fade in timeout={800}>
            <Box>
              <Box textAlign="center" mb={4}>
                <Typography
                  variant="h4"
                  component="h1"
                  gutterBottom
                  sx={{
                    background: 'linear-gradient(45deg, #4299e1 30%, #63b3ed 90%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    mb: 2,
                  }}
                >
                  Sistema Inteligente VR/VA
                </Typography>
                <Typography
                  variant="body1"
                  color="text.secondary"
                  sx={{ maxWidth: 600, mx: 'auto' }}
                >
                  Processamento automatizado de Vale Refeição e Vale Alimentação
                  usando inteligência artificial multi-agente
                </Typography>
              </Box>

              <Card sx={{ mb: 4, overflow: 'visible' }}>
                <CardContent sx={{ p: 3 }}>
                  <Stepper
                    activeStep={activeStep}
                    orientation="horizontal"
                    sx={{ mb: 4 }}
                  >
                    {steps.map((step, index) => {
                      const StepIcon = step.icon;
                      return (
                        <Step key={step.label}>
                          <StepLabel
                            StepIconComponent={() => (
                              <Box
                                sx={{
                                  width: 40,
                                  height: 40,
                                  borderRadius: '50%',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  bgcolor: index <= activeStep ? 'primary.main' : 'grey.300',
                                  color: index <= activeStep ? 'white' : 'grey.600',
                                  transition: 'all 0.3s ease',
                                }}
                              >
                                <StepIcon fontSize="small" />
                              </Box>
                            )}
                          >
                            <Typography
                              variant="body2"
                              sx={{
                                fontWeight: index === activeStep ? 600 : 400,
                                color: index <= activeStep ? 'text.primary' : 'text.secondary',
                              }}
                            >
                              {step.label}
                            </Typography>
                          </StepLabel>
                        </Step>
                      );
                    })}
                  </Stepper>

                  {error && (
                    <Slide direction="up" in={!!error}>
                      <Alert
                        severity="error"
                        sx={{ mb: 3 }}
                        onClose={() => setError(null)}
                      >
                        {error}
                      </Alert>
                    </Slide>
                  )}

                  <Box sx={{ minHeight: 400 }}>
                    {renderStepContent(activeStep)}
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
                    <Button
                      onClick={handleBack}
                      disabled={activeStep === 0}
                      variant="outlined"
                      sx={{
                        minWidth: 120,
                        opacity: activeStep === 0 ? 0 : 1,
                        transition: 'opacity 0.3s ease',
                      }}
                    >
                      Voltar
                    </Button>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      {activeStep < steps.length - 1 && !processing && (
                        <Chip
                          icon={<InfoIcon />}
                          label={`Passo ${activeStep + 1} de ${steps.length}`}
                          variant="outlined"
                          size="small"
                        />
                      )}
                      {processing && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CircularProgress size={20} />
                          <Typography variant="body2" color="text.secondary">
                            Processando...
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </Box>
                </CardContent>
              </Card>

              {results && (
                <Fade in timeout={1000}>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={3}>
                      <Card>
                        <CardContent sx={{ textAlign: 'center', py: 3 }}>
                          <PeopleIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                          <Typography variant="h6" component="div">
                            {results.funcionarios_elegiveis || 0}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Funcionários Elegíveis
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Card>
                        <CardContent sx={{ textAlign: 'center', py: 3 }}>
                          <MoneyIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                          <Typography variant="h6" component="div">
                            R$ {results.valor_total_vr?.toLocaleString('pt-BR') || '0'}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Valor Total VR
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Card>
                        <CardContent sx={{ textAlign: 'center', py: 3 }}>
                          <CompanyIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                          <Typography variant="h6" component="div">
                            R$ {results.valor_empresa?.toLocaleString('pt-BR') || '0'}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Valor Empresa
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Card>
                        <CardContent sx={{ textAlign: 'center', py: 3 }}>
                          <TimeIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                          <Typography variant="h6" component="div">
                            {results.tempo_processamento || 'N/A'}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Tempo de Processamento
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Fade>
              )}
            </Box>
          </Fade>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;