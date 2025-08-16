import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  Chip,
  IconButton
} from '@mui/material';
import {
  Download,
  Refresh,
  CheckCircle,
  TableChart,
  AttachMoney,
  People,
  Schedule,
  Share
} from '@mui/icons-material';

interface ResultsViewProps {
  results: any;
  onNewProcess: () => void;
}

const ResultsView: React.FC<ResultsViewProps> = ({ results, onNewProcess }) => {
  if (!results) {
    return (
      <Alert severity="error">
        Nenhum resultado disponível para exibição.
      </Alert>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  const handleDownload = async (fileName: string) => {
    try {
      const response = await fetch(`/api/download/${fileName}`);
      
      if (!response.ok) {
        throw new (Error as any)('Erro no download do arquivo');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      alert(`Download concluído: ${fileName}`);
    } catch (error: any) {
      alert(`Erro no download: ${error.message}`);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Status do Processamento */}
      <Alert 
        severity="success" 
        icon={<CheckCircle />}
        action={
          <Button color="inherit" size="small" onClick={onNewProcess}>
            Novo Processamento
          </Button>
        }
      >
        Processamento concluído com sucesso em {results.tempo_processamento}! 
        Todos os arquivos foram gerados conforme especificações.
      </Alert>

      {/* Estatísticas Principais */}
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Card elevation={3} sx={{ flex: '1 1 200px' }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <People sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h4" color="primary">
              {formatNumber(results.funcionarios_elegiveis)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Funcionários Elegíveis
            </Typography>
          </CardContent>
        </Card>
        
        <Card elevation={3} sx={{ flex: '1 1 200px' }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <AttachMoney sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
            <Typography variant="h4" color="success.main">
              {formatCurrency(results.valor_total_vr)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Valor Total VR
            </Typography>
          </CardContent>
        </Card>
        
        <Card elevation={3} sx={{ flex: '1 1 200px' }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Schedule sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
            <Typography variant="h4" color="info.main">
              {formatCurrency(results.valor_empresa)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Custo Empresa (80%)
            </Typography>
          </CardContent>
        </Card>
        
        <Card elevation={3} sx={{ flex: '1 1 200px' }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <AttachMoney sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
            <Typography variant="h4" color="warning.main">
              {formatCurrency(results.valor_funcionario)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Desconto Funcionário (20%)
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Arquivos Gerados */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Arquivos Gerados
          </Typography>
          <List>
            {results.arquivos_gerados.map((arquivo: string, index: number) => (
              <ListItem
                key={index}
                secondaryAction={
                  <Box>
                    <IconButton onClick={() => handleDownload(arquivo)} color="primary">
                      <Download />
                    </IconButton>
                    <IconButton color="default">
                      <Share />
                    </IconButton>
                  </Box>
                }
              >
                <ListItemIcon>
                  <TableChart color="success" />
                </ListItemIcon>
                <ListItemText
                  primary={arquivo}
                  secondary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                      <Chip 
                        label="Excel" 
                        size="small" 
                        color="primary" 
                        variant="outlined" 
                      />
                      <Chip 
                        label="Pronto" 
                        size="small" 
                        color="success" 
                      />
                      <Typography variant="caption" color="text.secondary">
                        {new Date().toLocaleString()}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Ações Rápidas */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button
          variant="contained"
          startIcon={<Download />}
          onClick={() => handleDownload('VR MENSAL 05.2025 vfinal.xlsx')}
          size="large"
        >
          Download Planilha Final
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={onNewProcess}
          size="large"
        >
          Novo Processamento
        </Button>
      </Box>
    </Box>
  );
};

export default ResultsView;