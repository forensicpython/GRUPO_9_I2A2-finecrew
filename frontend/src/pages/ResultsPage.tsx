import React, { useState, useEffect, useCallback } from 'react';
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

  const handleDownload = useCallback(async (filename: string) => {
    // Evitar downloads duplicados
    if (downloadingFiles.has(filename)) {
      showNotification('Download já em andamento para este arquivo', 'info');
      return;
    }

    try {
      console.log(`🔄 Iniciando download: ${filename}`);
      console.log(`🌐 URL atual da página: ${window.location.href}`);
      console.log(`🌍 Origin: ${window.location.origin}`);

      // Marcar como baixando
      setDownloadingFiles(prev => new Set(prev).add(filename));

      // Fazer o download (usando URL relativa para aproveitar o proxy)
      const downloadUrl = `/api/download/${encodeURIComponent(filename)}`;

      console.log(`🔄 Fazendo requisição para: ${downloadUrl}`);
      console.log(`🔗 URL completa: ${window.location.origin}${downloadUrl}`);

      // Método mais robusto usando fetch
      const response = await fetch(downloadUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream,*/*',
        },
      });

      console.log(`📡 Resposta recebida - Status: ${response.status}, StatusText: ${response.statusText}`);
      console.log(`📦 Response URL: ${response.url}`);
      console.log(`📦 Response type: ${response.type}`);
      console.log(`📦 Response OK: ${response.ok}`);

      // Log dos headers
      console.log(`📋 Headers da resposta:`);
      response.headers.forEach((value, key) => {
        console.log(`📋 Header ${key}: ${value}`);
      });

      if (!response.ok) {
        let errorData;
        try {
          const responseText = await response.text();
          console.log(`📝 Response body text: ${responseText}`);
          try {
            errorData = JSON.parse(responseText);
          } catch {
            errorData = { error: responseText || 'Erro desconhecido' };
          }
        } catch {
          errorData = { error: 'Erro desconhecido' };
        }
        throw new Error(errorData.error || `Erro ${response.status}: ${response.statusText}`);
      }

      // Obter o blob do arquivo
      console.log(`🔄 Criando blob do arquivo...`);
      const blob = await response.blob();

      console.log(`📦 Blob criado - Tamanho: ${blob.size} bytes, Tipo: ${blob.type}`);

      // Verificar se o blob não está vazio
      if (blob.size === 0) {
        throw new Error('Arquivo vazio recebido do servidor');
      }

      // Tentar download usando blob
      try {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';

        console.log(`🔗 Link criado - href: ${link.href}, download: ${link.download}`);

        // Adicionar ao DOM, clicar e remover
        document.body.appendChild(link);
        console.log(`🖱️ Simulando clique no link...`);
        link.click();
        document.body.removeChild(link);

        // Limpar URL temporária
        window.URL.revokeObjectURL(url);

        console.log(`✅ Download via blob concluído: ${filename}`);
        showNotification(`Download de "${filename}" concluído com sucesso!`, 'success');
      } catch (linkError) {
        console.warn(`⚠️ Falhou o download via blob, tentando método alternativo:`, linkError);

        // Fallback: usar window.location.href
        const fallbackUrl = `${window.location.origin}/api/download/${encodeURIComponent(filename)}`;
        console.log(`🔄 Tentando download direto via: ${fallbackUrl}`);
        window.location.href = fallbackUrl;

        console.log(`✅ Download direto iniciado: ${filename}`);
        showNotification(`Download de "${filename}" iniciado!`, 'success');
      }

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
  }, [downloadingFiles]);

  // Automatic download on results load
  useEffect(() => {
    if (results && results.arquivos_gerados && results.arquivos_gerados.length > 0) {
      // Find the main VR file (should be VR MENSAL 05.2025.xlsx)
      const mainVRFile = results.arquivos_gerados.find(file =>
        file.toLowerCase().includes('vr mensal') && file.toLowerCase().includes('.xlsx')
      );

      if (mainVRFile) {
        // Auto-download after 2 seconds to allow UI to render
        const timer = setTimeout(() => {
          console.log('🔄 Iniciando download automático:', mainVRFile);
          handleDownload(mainVRFile);
        }, 2000);

        return () => clearTimeout(timer);
      }
    }
  }, [results, handleDownload]);

  const showNotification = (message: string, severity: 'success' | 'error' | 'info') => {
    setNotification({ open: true, message, severity });
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

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
                  primary="Dados de funcionários processados"
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
              Arquivo Principal Gerado
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              📋 Processado em FinaCrew CrewAI
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