import React, { useState } from 'react';
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
  CircularProgress,
  Snackbar,
  Alert,
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
  const [downloadingFiles, setDownloadingFiles] = useState<Set<string>>(new Set());
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info';
  }>({ open: false, message: '', severity: 'info' });
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

  const showNotification = (message: string, severity: 'success' | 'error' | 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleDownload = async (filename: string) => {
    // Evitar downloads duplicados
    if (downloadingFiles.has(filename)) {
      showNotification('Download já em andamento para este arquivo', 'info');
      return;
    }

    try {
      console.log(`🔄 Iniciando download: ${filename}`);
      
      // Marcar como baixando
      setDownloadingFiles(prev => new Set(prev).add(filename));
      
      // Verificar se o arquivo existe primeiro
      const checkResponse = await fetch(`/api/files`);
      if (!checkResponse.ok) {
        throw new Error('Erro ao verificar arquivos disponíveis');
      }
      
      const { files } = await checkResponse.json();
      const fileExists = files.some((file: any) => file.name === filename);
      
      if (!fileExists) {
        const availableFiles = files.map((f: any) => f.name).join(', ');
        throw new Error(`Arquivo "${filename}" não encontrado. Disponíveis: ${availableFiles}`);
      }
      
      // Fazer o download
      const downloadUrl = `/api/download/${encodeURIComponent(filename)}`;
      
      // Método mais robusto usando fetch
      const response = await fetch(downloadUrl);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Erro desconhecido' }));
        throw new Error(errorData.error || `Erro ${response.status}: ${response.statusText}`);
      }
      
      // Obter o blob do arquivo
      const blob = await response.blob();
      
      // Verificar se o blob não está vazio
      if (blob.size === 0) {
        throw new Error('Arquivo vazio recebido do servidor');
      }
      
      // Criar link de download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      
      // Adicionar ao DOM, clicar e remover
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Limpar URL temporária
      window.URL.revokeObjectURL(url);
      
      console.log(`✅ Download concluído: ${filename}`);
      showNotification(`Download de "${filename}" concluído com sucesso!`, 'success');
      
    } catch (error) {
      console.error(`❌ Erro no download de "${filename}":`, error);
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      showNotification(`Erro ao baixar "${filename}": ${errorMessage}`, 'error');
    } finally {
      // Remover da lista de downloads em andamento
      setDownloadingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(filename);
        return newSet;
      });
    }
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
                        startIcon={downloadingFiles.has(filename) ? 
                          <CircularProgress size={16} /> : 
                          <DownloadIcon />
                        }
                        onClick={() => handleDownload(filename)}
                        color={isReport ? "success" : "primary"}
                        disabled={downloadingFiles.has(filename)}
                      >
                        {downloadingFiles.has(filename) ? 'Baixando...' : 'Baixar'}
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

      {/* Notificações */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification(prev => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setNotification(prev => ({ ...prev, open: false }))}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ResultsPage;