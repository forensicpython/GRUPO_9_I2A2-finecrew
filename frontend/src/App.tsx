import React, { useState } from 'react';
import {
  ThemeProvider,
  CssBaseline,
  Box,
  Container,
  Stepper,
  Step,
  StepLabel,
  Typography,
  Button,
  Paper,
  AppBar,
  Toolbar,
  LinearProgress,
} from '@mui/material';
import { theme } from './styles/theme';
import { AppState, GroqConfig, ProcessingResults } from './types';

// Páginas
import ConfigurationPage from './pages/ConfigurationPage';
import UploadPage from './pages/UploadPage';
import ProcessingPage from './pages/ProcessingPage';
import ResultsPage from './pages/ResultsPage';

const steps = ['Configuração', 'Upload', 'Processamento', 'Resultados'];

function App() {
  const [state, setState] = useState<AppState>({
    currentStep: 0,
    groqConfig: null,
    uploadedFiles: [],
    processing: false,
    results: null,
  });

  const updateState = (updates: Partial<AppState>) => {
    setState(prev => ({ ...prev, ...updates }));
  };

  const handleConfigComplete = (config: GroqConfig) => {
    updateState({ groqConfig: config });
    nextStep();
  };

  const handleFilesUploaded = (files: File[]) => {
    updateState({ uploadedFiles: files });
    // Não avançar automaticamente - deixar usuário decidir quando ir para processamento
  };

  const handleProcessingComplete = (results: ProcessingResults) => {
    updateState({ processing: false, results });
    nextStep();
  };

  const nextStep = () => {
    if (state.currentStep < steps.length - 1) {
      updateState({ currentStep: state.currentStep + 1 });
    }
  };

  const prevStep = () => {
    if (state.currentStep > 0) {
      updateState({ currentStep: state.currentStep - 1 });
    }
  };

  const resetProcess = () => {
    setState({
      currentStep: 0,
      groqConfig: null,
      uploadedFiles: [],
      processing: false,
      results: null,
    });
  };

  const getProgress = () => {
    return ((state.currentStep + 1) / steps.length) * 100;
  };

  const renderCurrentStep = () => {
    switch (state.currentStep) {
      case 0:
        return (
          <ConfigurationPage
            onConfigComplete={handleConfigComplete}
            initialConfig={state.groqConfig}
          />
        );
      case 1:
        return (
          <UploadPage
            onFilesUploaded={handleFilesUploaded}
            uploadedFiles={state.uploadedFiles}
          />
        );
      case 2:
        return (
          <ProcessingPage
            files={state.uploadedFiles}
            groqConfig={state.groqConfig}
            onComplete={handleProcessingComplete}
            processing={state.processing}
            setProcessing={(processing) => updateState({ processing })}
          />
        );
      case 3:
        return (
          <ResultsPage
            results={state.results}
            onReset={resetProcess}
          />
        );
      default:
        return <Typography>Etapa não encontrada</Typography>;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
        {/* Header */}
        <AppBar position="static" elevation={0}>
          <Toolbar>
            <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 700 }}>
              FinaCrew
            </Typography>
            <Typography variant="body2" color="inherit">
              Sistema de Processamento VR/VA
            </Typography>
          </Toolbar>
        </AppBar>

        {/* Progress Bar */}
        <LinearProgress
          variant="determinate"
          value={getProgress()}
          sx={{
            height: 4,
            bgcolor: 'rgba(99, 102, 241, 0.1)',
            '& .MuiLinearProgress-bar': {
              bgcolor: 'primary.main',
            },
          }}
        />

        <Container maxWidth="lg" sx={{ py: 4 }}>
          {/* Stepper */}
          <Paper sx={{ p: 3, mb: 4 }}>
            <Stepper activeStep={state.currentStep} alternativeLabel>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </Paper>

          {/* Conteúdo da Etapa */}
          <Paper sx={{ p: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom>
              {steps[state.currentStep]}
            </Typography>
            {renderCurrentStep()}
          </Paper>

          {/* Navegação */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Button
              onClick={prevStep}
              disabled={state.currentStep === 0}
              variant="outlined"
            >
              Anterior
            </Button>
            
            <Typography variant="body2" sx={{ alignSelf: 'center' }}>
              Etapa {state.currentStep + 1} de {steps.length}
            </Typography>

            <Button
              onClick={nextStep}
              disabled={
                state.currentStep === steps.length - 1 ||
                (state.currentStep === 1 && state.uploadedFiles.length === 0)
              }
              variant="contained"
            >
              {state.currentStep === steps.length - 1 ? 'Finalizar' : 'Próximo'}
            </Button>
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;