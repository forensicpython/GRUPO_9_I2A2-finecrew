import React, { useState } from 'react';
import { 
  ThemeProvider, 
  CssBaseline,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepConnector,
  stepConnectorClasses,
  StepIconProps,
  styled,
  IconButton,
  Fade,
  Grow
} from '@mui/material';
import { 
  AccountBalance, 
  Analytics, 
  CloudUpload,
  Settings,
  CheckCircle,
  DarkMode,
  LightMode
} from '@mui/icons-material';
import FileUploader from './components/FileUploader';
import ProcessingDashboard from './components/ProcessingDashboard';
import ResultsView from './components/ResultsView';
import ConfigurationStep, { GroqConfig } from './components/ConfigurationStep';
import { theme } from './styles/theme';
import './styles/animations.css';
import './App.css';

// Custom styled components
const GradientBox = styled(Box)(({ theme }) => ({
  background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #64748b 100%)',
  backgroundSize: '200% 200%',
  animation: 'gradientShift 15s ease infinite',
  color: 'white',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.05"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
    opacity: 0.4,
  }
}));

const ColorlibConnector = styled(StepConnector)(({ theme }) => ({
  [`&.${stepConnectorClasses.alternativeLabel}`]: {
    top: 22,
  },
  [`&.${stepConnectorClasses.active}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      backgroundImage: 'linear-gradient(95deg, rgb(59,130,246) 0%, rgb(30,64,175) 50%, rgb(100,116,139) 100%)',
    },
  },
  [`&.${stepConnectorClasses.completed}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      backgroundImage: 'linear-gradient(95deg, rgb(59,130,246) 0%, rgb(30,64,175) 50%, rgb(100,116,139) 100%)',
    },
  },
  [`& .${stepConnectorClasses.line}`]: {
    height: 3,
    border: 0,
    backgroundColor: theme.palette.mode === 'dark' ? theme.palette.grey[800] : '#eaeaf0',
    borderRadius: 1,
  },
}));

const ColorlibStepIconRoot = styled('div')<{
  ownerState: { completed?: boolean; active?: boolean };
}>(({ theme, ownerState }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? theme.palette.grey[700] : '#ccc',
  zIndex: 1,
  color: '#fff',
  width: 50,
  height: 50,
  display: 'flex',
  borderRadius: '50%',
  justifyContent: 'center',
  alignItems: 'center',
  ...(ownerState.active && {
    backgroundImage: 'linear-gradient(136deg, rgb(59,130,246) 0%, rgb(30,64,175) 50%, rgb(100,116,139) 100%)',
    boxShadow: '0 4px 10px 0 rgba(0,0,0,.25)',
  }),
  ...(ownerState.completed && {
    backgroundImage: 'linear-gradient(136deg, rgb(59,130,246) 0%, rgb(30,64,175) 50%, rgb(100,116,139) 100%)',
  }),
}));

function ColorlibStepIcon(props: StepIconProps) {
  const { active, completed, className } = props;

  const icons: { [index: string]: React.ReactElement } = {
    1: <Settings />,
    2: <CloudUpload />,
    3: <Analytics />,
    4: <CheckCircle />,
  };

  return (
    <ColorlibStepIconRoot ownerState={{ completed, active }} className={className}>
      {icons[String(props.icon)]}
    </ColorlibStepIconRoot>
  );
}

const steps = [
  'Configuração',
  'Upload dos Arquivos',
  'Processamento',
  'Resultados'
];

function App() {
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [groqConfig, setGroqConfig] = useState<GroqConfig | null>(null);

  const handleConfigurationComplete = (config: GroqConfig) => {
    setGroqConfig(config);
    setActiveStep(1);
  };

  const handleFilesUploaded = (files: File[]) => {
    setUploadedFiles(files);
    if (files.length >= 5) { // Mínimo 5 arquivos necessários
      setActiveStep(2);
    }
  };

  const handleProcessingComplete = (results: any) => {
    setResults(results);
    setProcessing(false);
    setActiveStep(3);
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <ConfigurationStep 
            onConfigurationComplete={handleConfigurationComplete}
            initialConfig={groqConfig || undefined}
          />
        );
      case 1:
        return (
          <FileUploader 
            onFilesUploaded={handleFilesUploaded}
            uploadedFiles={uploadedFiles}
          />
        );
      case 2:
        return (
          <ProcessingDashboard 
            files={uploadedFiles}
            onProcessingComplete={handleProcessingComplete}
            processing={processing}
            setProcessing={setProcessing}
            groqConfig={groqConfig}
          />
        );
      case 3:
        return (
          <ResultsView 
            results={results}
            onNewProcess={() => {
              setActiveStep(0);
              setUploadedFiles([]);
              setResults(null);
              setGroqConfig(null);
            }}
          />
        );
      default:
        return <div>Erro: Etapa não encontrada</div>;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
        {/* Header com gradiente */}
        <GradientBox>
          <AppBar position="static" elevation={0} sx={{ background: 'transparent' }}>
            <Toolbar sx={{ py: 2 }}>
              <AccountBalance sx={{ mr: 2, fontSize: 32 }} />
              <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
                FinaCrew
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Analytics />
                  <Typography variant="body2">
                    v2.1 Professional
                  </Typography>
                </Box>
              </Box>
            </Toolbar>
          </AppBar>

          <Container maxWidth="lg" sx={{ pb: 6, pt: 4 }}>
            <Fade in timeout={1000}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
                  Sistema de Processamento VR/VA
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9, maxWidth: 600, mx: 'auto' }}>
                  Automatize o cálculo de benefícios com inteligência artificial
                </Typography>
              </Box>
            </Fade>
          </Container>
        </GradientBox>

        {/* Conteúdo principal */}
        <Container maxWidth="xl" sx={{ mt: -4, mb: 4, position: 'relative', zIndex: 1 }}>
          {/* Card do Stepper */}
          <Grow in timeout={1200}>
            <Paper 
              elevation={3} 
              sx={{ 
                p: 4, 
                mb: 4, 
                borderRadius: 3,
                background: 'white',
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
              }}
              className="fade-in"
            >
              <Stepper 
                activeStep={activeStep} 
                alternativeLabel
                connector={<ColorlibConnector />}
              >
                {steps.map((label) => (
                  <Step key={label}>
                    <StepLabel StepIconComponent={ColorlibStepIcon}>{label}</StepLabel>
                  </Step>
                ))}
              </Stepper>
            </Paper>
          </Grow>

          {/* Conteúdo da etapa atual */}
          <Fade in timeout={800}>
            <Box className="fade-in-delayed">
              {renderStepContent()}
            </Box>
          </Fade>
        </Container>

        {/* Footer */}
        <Box 
          sx={{ 
            mt: 'auto', 
            py: 3, 
            px: 2, 
            background: 'linear-gradient(180deg, transparent 0%, #f8fafc 100%)',
            textAlign: 'center'
          }}
        >
          <Typography variant="body2" color="text.secondary">
            FinaCrew © 2025 - Sistema profissional de processamento automatizado
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ opacity: 0.7 }}>
            Desenvolvido com React, Material-UI e Inteligência Artificial
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
