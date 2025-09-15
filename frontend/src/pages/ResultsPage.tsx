import React from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Refresh as ResetIcon,
  Download as DownloadIcon,
  People as PeopleIcon,
  AttachMoney as MoneyIcon,
  Business as BusinessIcon,
  Person as PersonIcon,
  Schedule as TimeIcon,
  Description as FileIcon,
  Assignment as ReportIcon,
} from '@mui/icons-material';
import { ProcessingResults } from '../types';

interface ResultsPageProps {
  results: ProcessingResults | null;
  onReset: () => void;
}

const ResultsPage: React.FC<ResultsPageProps> = ({
  results,
  onReset,
}) => {
  if (!results) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="text.secondary">
          Nenhum resultado disponível
        </Typography>
        <Button
          variant="contained"
          onClick={onReset}
          sx={{ mt: 2 }}
          startIcon={<ResetIcon />}
        >
          Iniciar Novo Processamento
        </Button>
      </Box>
    );
  }

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const handleDownload = (filename: string) => {
    const link = document.createElement('a');
    link.href = `/api/download/${encodeURIComponent(filename)}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Box>
      <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
        Processamento concluído! Confira os resultados e baixe os arquivos gerados.
      </Typography>

      {/* Métricas Principais */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 4 }}>
        <Card>
          <CardContent sx={{ textAlign: 'center' }}>
            <PeopleIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h4" color="primary.main" gutterBottom>
              {results.funcionarios_elegiveis.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Funcionários Elegíveis
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent sx={{ textAlign: 'center' }}>
            <MoneyIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
            <Typography variant="h4" color="success.main" gutterBottom>
              {formatCurrency(results.valor_total_vr)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Valor Total VR
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent sx={{ textAlign: 'center' }}>
            <BusinessIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
            <Typography variant="h4" color="warning.main" gutterBottom>
              {formatCurrency(results.valor_empresa)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Valor Empresa
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent sx={{ textAlign: 'center' }}>
            <PersonIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
            <Typography variant="h4" color="info.main" gutterBottom>
              {formatCurrency(results.valor_funcionario)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Valor Funcionário
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Detalhes e Arquivos */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        {/* Informações do Processamento */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Detalhes do Processamento
            </Typography>
            
            <List>
              <ListItem>
                <ListItemIcon>
                  <TimeIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Tempo de Processamento"
                  secondary={results.tempo_processamento}
                />
              </ListItem>
              
              <Divider />
              
              <ListItem>
                <ListItemIcon>
                  <PeopleIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Funcionários Processados"
                  secondary={`${results.funcionarios_elegiveis} funcionários elegíveis para VR/VA`}
                />
              </ListItem>
              
              <Divider />
              
              <ListItem>
                <ListItemIcon>
                  <MoneyIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Distribuição de Custos"
                  secondary={
                    <Box sx={{ mt: 1 }}>
                      <Chip
                        label={`Empresa: ${formatCurrency(results.valor_empresa)}`}
                        size="small"
                        sx={{ mr: 1, mb: 1 }}
                      />
                      <Chip
                        label={`Funcionário: ${formatCurrency(results.valor_funcionario)}`}
                        size="small"
                        sx={{ mb: 1 }}
                      />
                    </Box>
                  }
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        {/* Arquivos Gerados */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Arquivos Gerados
            </Typography>
            
            <List>
              {results.arquivos_gerados.map((filename, index) => {
                const isReport = filename.toLowerCase().includes('relatorio') || filename.endsWith('.txt');
                return (
                  <ListItem
                    key={index}
                    secondaryAction={
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<DownloadIcon />}
                        onClick={() => handleDownload(filename)}
                        color={isReport ? "success" : "primary"}
                      >
                        Baixar
                      </Button>
                    }
                  >
                    <ListItemIcon>
                      {isReport ? (
                        <ReportIcon color="success" />
                      ) : (
                        <FileIcon color="primary" />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={filename}
                      secondary={
                        isReport 
                          ? `📊 Relatório Contábil - ${results.tempo_processamento}` 
                          : `Arquivo processado em ${results.tempo_processamento}`
                      }
                    />
                  </ListItem>
                )
              })}
            </List>

            {results.arquivos_gerados.length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                Nenhum arquivo foi gerado durante o processamento
              </Typography>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Ações */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Button
          variant="contained"
          size="large"
          onClick={onReset}
          startIcon={<ResetIcon />}
        >
          Processar Novos Arquivos
        </Button>
      </Box>
    </Box>
  );
};

export default ResultsPage;